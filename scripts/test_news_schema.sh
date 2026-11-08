#!/bin/sh
# Runs against a disposable local container; never connects to the hosted project.
set -eu
container="vitemind-news-schema-test-$$"
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cleanup() { docker rm -f "$container" >/dev/null 2>&1 || true; }
trap cleanup EXIT INT TERM
docker run -d --name "$container" --network none -e POSTGRES_PASSWORD=local-test-only postgres:17.6 >/dev/null
ready=0
for attempt in $(seq 1 30); do
  case "$(docker logs "$container" 2>&1)" in
    *'PostgreSQL init process complete; ready for start up.'*)
      if docker exec "$container" pg_isready -U postgres >/dev/null 2>&1; then ready=1; break; fi ;;
  esac
  sleep 1
done
[ "$ready" -eq 1 ] || { echo 'Local PostgreSQL did not become ready' >&2; exit 1; }
docker exec -i "$container" psql -X -v ON_ERROR_STOP=1 -U postgres <<'SQL'
create role anon nologin;
create role authenticated nologin;
create role service_role nologin bypassrls;
create schema auth;
create table auth.users (id uuid primary key);
create function auth.uid() returns uuid language sql stable as $$
  select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid
$$;
grant usage on schema auth to anon, authenticated, service_role;
create table public.rss_feeds (id integer primary key, name text);
create table public.news (id integer primary key, title text);
insert into public.rss_feeds values (1, 'preserved feed');
insert into public.news values (1, 'preserved article');
insert into auth.users values ('11111111-1111-1111-1111-111111111111'), ('22222222-2222-2222-2222-222222222222');
SQL
docker exec -i "$container" psql -X -v ON_ERROR_STOP=1 -U postgres < "$root/supabase/migrations/20261101074245_news_subscription_foundation.sql"
docker exec -i "$container" psql -X -v ON_ERROR_STOP=1 -U postgres <<'SQL'
insert into public.news_admins (user_id) values ('11111111-1111-1111-1111-111111111111');
insert into public.published_news (title, summary, link, content_type) values ('Public', 'Summary', 'https://example.com', 'project');
insert into public.published_news (title, summary, link, content_type, withdrawn_at) values ('Withdrawn', 'Summary', 'https://example.com/old', 'project', now());
do $$ begin
  if (select count(*) from public.rss_feeds) != 1 or (select count(*) from public.news) != 1 then
    raise exception 'existing rows changed';
  end if;
  if (select review_required from public.news_review_settings) is distinct from false then
    raise exception 'review default is not off';
  end if;
end $$;
set role anon;
do $$ begin
  if (select count(*) from public.published_news) != 1 then raise exception 'anonymous published visibility failed'; end if;
  begin
    perform * from public.news_review_settings;
    raise exception 'anonymous user can read settings';
  exception when insufficient_privilege then null; end;
end $$;
reset role;
set role authenticated;
select set_config('request.jwt.claim.sub', '22222222-2222-2222-2222-222222222222', false);
do $$ declare affected integer; begin
  if (select count(*) from public.news_review_settings) != 0 then raise exception 'non-admin can read settings'; end if;
  update public.news_review_settings set review_required = true;
  get diagnostics affected = row_count;
  if affected != 0 then raise exception 'non-admin can change settings'; end if;
  if (select count(*) from public.published_news) != 1 then raise exception 'non-admin sees withdrawn news'; end if;
end $$;
select set_config('request.jwt.claim.sub', '11111111-1111-1111-1111-111111111111', false);
do $$ declare affected integer; begin
  update public.news_review_settings set review_required = true;
  get diagnostics affected = row_count;
  if affected != 1 then raise exception 'admin cannot update settings'; end if;
  insert into public.news_blocked_keywords (keyword, content_type) values ('广告', 'tutorial');
  if (select count(*) from public.news_review_events where actor_id = auth.uid()) != 2 then
    raise exception 'settings changes were not audited with the current actor';
  end if;
  begin
    insert into public.news_review_events (action) values ('forged');
    raise exception 'client can forge audit entries';
  exception when insufficient_privilege then null; end;
  if (select count(*) from public.published_news) != 2 then raise exception 'admin cannot see withdrawn news'; end if;
end $$;
reset role;
SQL
docker exec -i "$container" psql -X -v ON_ERROR_STOP=1 -U postgres <<'SQL'
insert into public.news_candidates (id, source_type, source_id, source_item_id, link, title, summary, source_excerpt,
  content_type, source_published_at, status, source_validated, link_verified, tutorial_evidence_verified)
values
 ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'rss', 's', 'a', 'https://example.com/a', 'Agent A', 'summary', 'excerpt', 'project', now(), 'new', true, true, false),
 ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 'rss', 's', 'b', 'https://example.com/b', '广告', 'summary', 'excerpt', 'tutorial', now(), 'new', true, true, true),
 ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3', 'rss', 's', 'c', 'https://example.com/c', 'Agent C', 'summary', 'excerpt', 'project', now(), 'pending', true, true, false),
 ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4', 'rss', 's', 'd', 'https://example.com/d', 'Agent D', 'summary', 'excerpt', 'project', now(), 'new', true, false, false);
-- Earlier checks turned review on. Automatic publication must fail without changing data.
set role service_role;
do $$ declare failed boolean := false; begin
  begin perform public.news_publish_candidates(array['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1'::uuid], 'automatic');
  exception when raise_exception then failed := true; end;
  if not failed then raise exception 'automatic publication ignored review setting'; end if;
end $$;
reset role;
update public.news_review_settings set review_required = false;
set role service_role;
do $$ declare failed boolean := false; begin
  perform public.news_publish_candidates(array['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1'::uuid], 'automatic');
  perform public.news_publish_candidates(array['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1'::uuid], 'automatic');
  if (select count(*) from public.published_news where candidate_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1') != 1 then
    raise exception 'repeated publication was not idempotent';
  end if;
  begin perform public.news_publish_candidates(array['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2'::uuid], 'automatic');
  exception when raise_exception then failed := true; end;
  if not failed then raise exception 'blocked keyword was ignored'; end if;
  failed := false;
  begin perform public.news_publish_candidates(array['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3'::uuid], 'automatic');
  exception when raise_exception then failed := true; end;
  if not failed then raise exception 'pending candidate published automatically'; end if;
  failed := false;
  begin perform public.news_publish_candidates(array['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4'::uuid], 'automatic');
  exception when raise_exception then failed := true; end;
  if not failed then raise exception 'unverified link published'; end if;
end $$;
reset role;
set role authenticated;
select set_config('request.jwt.claim.sub', '22222222-2222-2222-2222-222222222222', false);
do $$ declare failed boolean := false; begin
  begin perform public.news_publish_candidates(array['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3'::uuid], 'manual');
  exception when insufficient_privilege then failed := true; end;
  if not failed then raise exception 'non-admin was able to publish'; end if;
end $$;
select set_config('request.jwt.claim.sub', '11111111-1111-1111-1111-111111111111', false);
select public.news_publish_candidates(array['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3'::uuid], 'manual');
reset role;
insert into public.news_candidates (id, source_type, source_id, source_item_id, link, title, summary, source_excerpt,
  content_type, source_published_at, status, source_validated, link_verified)
values
 ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5', 'rss', 's', 'e', 'https://example.com/e', 'Agent E', 'summary', 'excerpt', 'project', now(), 'new', true, true),
 ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa6', 'rss', 's', 'f', 'https://example.com/f', 'Agent F', 'summary', 'excerpt', 'project', now(), 'new', true, true),
 ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa7', 'rss', 's', 'g', 'https://example.com/g', 'Agent G', 'summary', 'excerpt', 'project', now(), 'new', true, true);
set role service_role;
do $$ declare failed boolean := false; begin
  begin perform public.news_publish_candidates(array['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2'::uuid], 'automatic');
  exception when raise_exception then failed := true; end;
  if not failed or exists (select 1 from public.published_news where candidate_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5') then
    raise exception 'invalid batch did not roll back';
  end if;
  failed := false;
  begin perform public.news_publish_candidates(array['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa6'::uuid, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa7'::uuid], 'automatic');
  exception when raise_exception then failed := true; end;
  if not failed or exists (select 1 from public.published_news where candidate_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5') then
    raise exception 'daily limit or atomicity failed';
  end if;
end $$;
reset role;
SQL
docker exec "$container" psql -X -v ON_ERROR_STOP=1 -U postgres -c "begin; set role service_role; select public.news_publish_candidates(array['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5'::uuid], 'automatic'); select pg_sleep(1); commit" >/dev/null 2>&1 &
first=$!
docker exec "$container" psql -X -v ON_ERROR_STOP=1 -U postgres -c "begin; set role service_role; select public.news_publish_candidates(array['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa6'::uuid], 'automatic'); commit" >/dev/null 2>&1 &
second=$!
wait "$first" || true
wait "$second" || true
concurrent_count=$(docker exec "$container" psql -X -A -t -U postgres -c "select count(*) from public.published_news where candidate_id in ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa6')")
[ "$concurrent_count" = 1 ] || { echo 'Concurrent publication did not enforce the daily limit' >&2; exit 1; }
docker exec -i "$container" psql -X -v ON_ERROR_STOP=1 -U postgres <<'SQL'
update public.published_news set published_at = now() - interval '2 days';
insert into public.published_news (title, summary, link, content_type) values ('Opinion', 'Summary', 'https://example.com/opinion', 'opinion');
insert into public.news_candidates (id, source_type, source_id, source_item_id, link, title, summary, source_excerpt,
  content_type, source_published_at, status, source_validated, link_verified)
values ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa8', 'rss', 's', 'h', 'https://example.com/h',
        'Opinion H', 'summary', 'excerpt', 'opinion', now(), 'new', true, true);
set role service_role;
do $$ declare failed boolean := false; begin
  begin perform public.news_publish_candidates(array['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa8'::uuid], 'automatic');
  exception when raise_exception then failed := true; end;
  if not failed then raise exception 'daily opinion limit was ignored'; end if;
end $$;
reset role;
SQL
docker exec -i "$container" psql -X -v ON_ERROR_STOP=1 -U postgres <<'SQL'
set role service_role;
do $$ declare inserted integer; begin
  select count(*) into inserted from public.news_ingest_candidates(
    '[{"candidate_id":"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1","source_type":"rss","source_id":"s","source_item_id":"import-1","title":"Original","link":"https://example.com/import-1"}]'::jsonb,
    'cccccccc-cccc-cccc-cccc-cccccccccccc');
  if inserted != 1 then raise exception 'initial import failed'; end if;
  select count(*) into inserted from public.news_ingest_candidates(
    '[{"candidate_id":"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1","source_type":"rss","source_id":"s","source_item_id":"import-1","title":"Overwrite","link":"https://example.com/import-1"}]'::jsonb,
    'dddddddd-dddd-dddd-dddd-dddddddddddd');
  if inserted != 0 then raise exception 'duplicate import was not ignored'; end if;
end $$;
reset role;
set role authenticated;
select set_config('request.jwt.claim.sub', '11111111-1111-1111-1111-111111111111', false);
update public.news_candidates set title = 'Admin edit' where id = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1';
do $$ declare failed boolean := false; begin
  begin update public.news_candidates set link_verified = true where id = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1';
  exception when insufficient_privilege then failed := true; end;
  if not failed then raise exception 'admin can forge link verification'; end if;
  failed := false;
  begin update public.news_candidates set status = 'published' where id = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1';
  exception when insufficient_privilege then failed := true; end;
  if not failed then raise exception 'admin can bypass publication transaction'; end if;
end $$;
reset role;
set role service_role;
do $$ declare failed boolean := false; begin
  begin perform public.news_finalize_candidates(
    '[{"candidate_id":"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1","title":"Model overwrite","status":"new"}]'::jsonb,
    'cccccccc-cccc-cccc-cccc-cccccccccccc');
  exception when raise_exception then failed := true; end;
  if not failed or (select title from public.news_candidates where id = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1') != 'Admin edit' then
    raise exception 'concurrent admin edit was overwritten';
  end if;
  perform public.news_ingest_candidates(
    '[{"candidate_id":"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2","source_type":"rss","source_id":"s","source_item_id":"import-2","title":"Original","link":"https://example.com/import-2"}]'::jsonb,
    'cccccccc-cccc-cccc-cccc-cccccccccccc');
  perform public.news_finalize_candidates(
    '[{"candidate_id":"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2","title":"Validated","summary":"Summary","source_excerpt":"Excerpt","content_type":"project","source_validated":true,"link_verified":true,"status":"new"}]'::jsonb,
    'cccccccc-cccc-cccc-cccc-cccccccccccc');
  if not exists (select 1 from public.news_candidates where id = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2'
    and title = 'Validated' and status = 'new' and revision = 1 and source_validated and link_verified) then
    raise exception 'candidate finalization failed';
  end if;
end $$;
reset role;
set role authenticated;
select set_config('request.jwt.claim.sub', '11111111-1111-1111-1111-111111111111', false);
update public.news_candidates set link = 'https://example.com/changed', content_type = 'tutorial'
  where id = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2';
do $$ begin
  if exists (select 1 from public.news_candidates where id = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2'
    and (link_verified or tutorial_evidence_verified)) then
    raise exception 'changing the link or type did not invalidate verification';
  end if;
end $$;
reset role;
SQL
docker exec -i "$container" psql -X -v ON_ERROR_STOP=1 -U postgres <<'SQL'
insert into public.news_candidates (id, source_type, source_id, source_item_id, link, title, summary, source_excerpt,
  content_type, source_published_at, status, duplicate_suspected)
values ('dddddddd-dddd-dddd-dddd-ddddddddddd1', 'rss', 's', 'review', 'https://example.com/review',
        'Review', 'Summary', 'Steps and code', 'tutorial', now(), 'pending', true);
set role authenticated;
select set_config('request.jwt.claim.sub', '22222222-2222-2222-2222-222222222222', false);
do $$ declare failed boolean := false; begin
  begin perform public.news_review_candidate('dddddddd-dddd-dddd-dddd-ddddddddddd1', 0, 'attest', null, true, true);
  exception when insufficient_privilege then failed := true; end;
  if not failed then raise exception 'non-admin could review candidate'; end if;
end $$;
select set_config('request.jwt.claim.sub', '11111111-1111-1111-1111-111111111111', false);
do $$ declare failed boolean := false; begin
  begin perform public.news_review_candidate('dddddddd-dddd-dddd-dddd-ddddddddddd1', 0, 'attest', null, false, false);
  exception when raise_exception then failed := true; end;
  if not failed then raise exception 'unconfirmed tutorial and duplicate passed review'; end if;
  perform public.news_review_candidate('dddddddd-dddd-dddd-dddd-ddddddddddd1', 0, 'attest', null, true, true);
  if not exists (select 1 from public.news_candidates where id = 'dddddddd-dddd-dddd-dddd-ddddddddddd1'
    and link_verified and source_validated and tutorial_evidence_verified and not duplicate_suspected and revision = 1) then
    raise exception 'review attestation was not recorded';
  end if;
  failed := false;
  begin perform public.news_review_candidate('dddddddd-dddd-dddd-dddd-ddddddddddd1', 0, 'reject', 'irrelevant', false, false);
  exception when raise_exception then failed := true; end;
  if not failed then raise exception 'stale review was accepted'; end if;
  perform public.news_review_candidate('dddddddd-dddd-dddd-dddd-ddddddddddd1', 1, 'reject', 'irrelevant', false, false);
  perform public.news_review_candidate('dddddddd-dddd-dddd-dddd-ddddddddddd1', 2, 'restore', null, false, false);
  if not exists (select 1 from public.news_candidates where id = 'dddddddd-dddd-dddd-dddd-ddddddddddd1'
    and status = 'pending' and revision = 3 and rejection_reason is null) then
    raise exception 'reject and restore transition failed';
  end if;
end $$;
reset role;
SQL
echo 'Isolated schema and RLS checks passed.'
