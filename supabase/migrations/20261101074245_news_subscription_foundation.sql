-- Additive foundation only. Existing news and rss_feeds are intentionally untouched.
-- Bootstrap the confirmed administrator separately after verifying its auth.users ID.
create table public.news_admins (
  user_id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);

create table public.news_review_settings (
  id boolean primary key default true check (id),
  review_required boolean not null default false,
  updated_at timestamptz not null default now(),
  updated_by uuid references auth.users(id)
);
insert into public.news_review_settings (id) values (true);

create table public.news_blocked_keywords (
  id bigint generated always as identity primary key,
  keyword text not null check (length(trim(keyword)) between 1 and 200),
  content_type text check (content_type in ('technical_update', 'tutorial', 'project', 'opinion')),
  enabled boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  updated_by uuid references auth.users(id)
);
create unique index news_blocked_keywords_unique on public.news_blocked_keywords
  (lower(trim(keyword)), coalesce(content_type, ''));

create table public.news_review_events (
  id bigint generated always as identity primary key,
  actor_id uuid references auth.users(id),
  action text not null,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- Legacy RSS feeds remain in rss_feeds; this registry is for additional connectors.
create table public.news_sources (
  id uuid primary key default gen_random_uuid(),
  name text not null check (length(trim(name)) > 0),
  source_type text not null check (source_type in ('github', 'mcp', 'skill', 'social')),
  config jsonb not null default '{}'::jsonb check (jsonb_typeof(config) = 'object'),
  enabled boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.news_candidates (
  id uuid primary key default gen_random_uuid(),
  source_type text not null check (source_type in ('rss', 'github', 'mcp', 'skill', 'social')),
  source_id text not null,
  source_item_id text not null,
  source_name text,
  link text not null,
  title text not null,
  summary_raw text,
  summary text,
  detail text,
  source_excerpt text,
  content_type text check (content_type in ('technical_update', 'tutorial', 'project', 'opinion')),
  suggested_content_type text check (suggested_content_type in ('technical_update', 'tutorial', 'project', 'opinion')),
  source_published_at timestamptz,
  source_updated_at timestamptz,
  first_seen_at timestamptz not null default now(),
  status text not null default 'new' check (status in ('new', 'pending', 'selected', 'rejected', 'published', 'withdrawn')),
  duplicate_suspected boolean not null default false,
  decision_reason text,
  matched_keywords text[] not null default '{}',
  import_token uuid,
  revision bigint not null default 0 check (revision >= 0),
  source_validated boolean not null default false,
  link_verified boolean not null default false,
  tutorial_evidence_verified boolean not null default false,
  rejection_reason text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (source_type, source_id, source_item_id)
);
create index news_candidates_status_seen on public.news_candidates (status, first_seen_at desc);

create table public.news_source_runs (
  id bigint generated always as identity primary key,
  source_type text not null,
  source_id text not null,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  status text not null check (status in ('ok', 'error')),
  item_count integer not null default 0 check (item_count >= 0),
  error_message text
);

create table public.published_news (
  id uuid primary key default gen_random_uuid(),
  candidate_id uuid unique references public.news_candidates(id),
  title text not null,
  summary text not null,
  detail text,
  link text not null,
  content_type text not null check (content_type in ('technical_update', 'tutorial', 'project', 'opinion', 'unknown')),
  published_at timestamptz not null default now(),
  withdrawn_at timestamptz
);
create index published_news_active_date on public.published_news (published_at desc) where withdrawn_at is null;

alter table public.news_admins enable row level security;
alter table public.news_review_settings enable row level security;
alter table public.news_blocked_keywords enable row level security;
alter table public.news_review_events enable row level security;
alter table public.news_sources enable row level security;
alter table public.news_candidates enable row level security;
alter table public.news_source_runs enable row level security;
alter table public.published_news enable row level security;

revoke all on public.news_admins, public.news_review_settings, public.news_blocked_keywords, public.news_review_events,
  public.news_sources, public.news_candidates, public.news_source_runs, public.published_news
  from public, anon, authenticated;
grant select on public.news_admins to authenticated;
grant select, update on public.news_review_settings to authenticated;
grant select, insert, update, delete on public.news_blocked_keywords, public.news_sources to authenticated;
grant select on public.news_review_events to authenticated;
grant select on public.news_candidates to authenticated;
grant update (title, summary, detail, link, content_type, rejection_reason) on public.news_candidates to authenticated;
grant select on public.news_source_runs to authenticated;
grant select on public.published_news to anon, authenticated;
grant all on public.news_admins, public.news_review_settings, public.news_blocked_keywords, public.news_review_events,
  public.news_sources, public.news_candidates, public.news_source_runs, public.published_news to service_role;
grant usage, select on sequence public.news_blocked_keywords_id_seq, public.news_source_runs_id_seq, public.news_review_events_id_seq to service_role;
grant usage, select on sequence public.news_blocked_keywords_id_seq to authenticated;

create policy "admins see their own membership" on public.news_admins for select to authenticated
  using (user_id = (select auth.uid()));

-- Membership is checked for every operation; signed-in alone is not sufficient.
create policy "admins read settings" on public.news_review_settings for select to authenticated
  using (exists (select 1 from public.news_admins where user_id = (select auth.uid())));
create policy "admins update settings" on public.news_review_settings for update to authenticated
  using (exists (select 1 from public.news_admins where user_id = (select auth.uid())))
  with check (exists (select 1 from public.news_admins where user_id = (select auth.uid())));

create policy "admins manage blocked keywords" on public.news_blocked_keywords for all to authenticated
  using (exists (select 1 from public.news_admins where user_id = (select auth.uid())))
  with check (exists (select 1 from public.news_admins where user_id = (select auth.uid())));
create policy "admins read review events" on public.news_review_events for select to authenticated
  using (exists (select 1 from public.news_admins where user_id = (select auth.uid())));
create policy "admins manage sources" on public.news_sources for all to authenticated
  using (exists (select 1 from public.news_admins where user_id = (select auth.uid())))
  with check (exists (select 1 from public.news_admins where user_id = (select auth.uid())));
create policy "admins manage candidates" on public.news_candidates for all to authenticated
  using (exists (select 1 from public.news_admins where user_id = (select auth.uid())))
  with check (exists (select 1 from public.news_admins where user_id = (select auth.uid())));
create policy "admins read source runs" on public.news_source_runs for select to authenticated
  using (exists (select 1 from public.news_admins where user_id = (select auth.uid())));
create policy "public reads published news" on public.published_news for select to anon, authenticated
  using (withdrawn_at is null);
create policy "admins read withdrawn news" on public.published_news for select to authenticated
  using (exists (select 1 from public.news_admins where user_id = (select auth.uid())));

-- Only the trigger can write this audit log; client roles cannot call the function.
create schema news_private;
revoke all on schema news_private from public, anon, authenticated;
create function news_private.stamp_news_settings() returns trigger
language plpgsql set search_path = pg_catalog as $$
begin
  new.updated_at := now();
  new.updated_by := auth.uid();
  return new;
end;
$$;
revoke all on function news_private.stamp_news_settings() from public, anon, authenticated;
create function news_private.lock_news_settings() returns trigger
language plpgsql set search_path = pg_catalog as $$
begin
  perform 1 from public.news_review_settings where id for update;
  if tg_op = 'DELETE' then return old; end if;
  return new;
end;
$$;
revoke all on function news_private.lock_news_settings() from public, anon, authenticated;
create trigger news_review_settings_stamp before update on public.news_review_settings
  for each row execute function news_private.stamp_news_settings();
create trigger news_blocked_keywords_stamp before insert or update on public.news_blocked_keywords
  for each row execute function news_private.stamp_news_settings();
create trigger news_blocked_keywords_lock before insert or update or delete on public.news_blocked_keywords
  for each row execute function news_private.lock_news_settings();

create function news_private.audit_news_settings() returns trigger
language plpgsql security definer set search_path = pg_catalog as $$
begin
  insert into public.news_review_events (actor_id, action, details)
  values (auth.uid(), tg_table_name || '.' || lower(tg_op),
    jsonb_build_object('before', case when tg_op = 'INSERT' then null else to_jsonb(old) end,
                       'after', case when tg_op = 'DELETE' then null else to_jsonb(new) end));
  return null;
end;
$$;
revoke all on function news_private.audit_news_settings() from public, anon, authenticated;
create trigger news_review_settings_audit after update on public.news_review_settings
  for each row execute function news_private.audit_news_settings();
create trigger news_blocked_keywords_audit after insert or update or delete on public.news_blocked_keywords
  for each row execute function news_private.audit_news_settings();
create trigger news_candidates_audit after update on public.news_candidates
  for each row execute function news_private.audit_news_settings();

create function news_private.bump_candidate_revision() returns trigger
language plpgsql set search_path = pg_catalog as $$
begin
  new.revision := old.revision + 1;
  new.updated_at := now();
  if current_setting('role', true) is distinct from 'service_role' then
    if new.link is distinct from old.link then
      new.link_verified := false;
    end if;
    if new.content_type is distinct from old.content_type then
      new.tutorial_evidence_verified := false;
    end if;
  end if;
  return new;
end;
$$;
revoke all on function news_private.bump_candidate_revision() from public, anon, authenticated;
create trigger news_candidates_revision before update on public.news_candidates
  for each row execute function news_private.bump_candidate_revision();

-- The ingestion service inserts once and can only finalize untouched imports
-- from its own run. Admin edits increment revision and win the race.
create function public.news_ingest_candidates(p_items jsonb, p_token uuid)
returns setof uuid language plpgsql set search_path = pg_catalog as $$
begin
  if current_setting('role', true) is distinct from 'service_role' then
    raise insufficient_privilege using message = 'Service role required';
  end if;
  if p_token is null or jsonb_typeof(p_items) is distinct from 'array' or jsonb_array_length(p_items) > 1000 then
    raise exception 'Invalid import batch';
  end if;
  return query
    insert into public.news_candidates (id, source_type, source_id, source_item_id, source_name, title, link,
      summary_raw, source_published_at, source_updated_at, first_seen_at, status, import_token)
    select (item->>'candidate_id')::uuid, item->>'source_type', item->>'source_id', item->>'source_item_id',
      item->>'source_name', item->>'title', item->>'link', item->>'summary_raw',
      nullif(item->>'published_at', '')::timestamptz, nullif(item->>'updated_at', '')::timestamptz,
      coalesce(nullif(item->>'first_seen_at', '')::timestamptz, now()), 'pending', p_token
    from jsonb_array_elements(p_items) item
    on conflict do nothing returning id;
end;
$$;
revoke all on function public.news_ingest_candidates(jsonb, uuid) from public, anon, authenticated;
grant execute on function public.news_ingest_candidates(jsonb, uuid) to service_role;

create function public.news_finalize_candidates(p_items jsonb, p_token uuid)
returns integer language plpgsql set search_path = pg_catalog as $$
declare expected integer; matched integer;
begin
  if current_setting('role', true) is distinct from 'service_role' then
    raise insufficient_privilege using message = 'Service role required';
  end if;
  if p_token is null or jsonb_typeof(p_items) is distinct from 'array' or jsonb_array_length(p_items) > 1000 then
    raise exception 'Invalid finalization batch';
  end if;
  expected := jsonb_array_length(p_items);
  if (select count(distinct item->>'candidate_id') from jsonb_array_elements(p_items) item) <> expected
     or exists (select 1 from jsonb_array_elements(p_items) item where item->>'status' not in ('new', 'pending') or item->>'status' is null) then
    raise exception 'Invalid finalization items';
  end if;
  perform 1 from public.news_candidates c where c.id in
    (select (item->>'candidate_id')::uuid from jsonb_array_elements(p_items) item) order by c.id for update;
  select count(*) into matched from public.news_candidates c where c.id in
    (select (item->>'candidate_id')::uuid from jsonb_array_elements(p_items) item)
    and c.import_token = p_token and c.revision = 0 and c.status = 'pending';
  if matched <> expected then raise exception 'Candidate changed since import'; end if;
  update public.news_candidates c set
    title = item->>'title', summary = item->>'summary', detail = item->>'detail',
    source_excerpt = item->>'source_excerpt', content_type = item->>'content_type',
    suggested_content_type = item->>'suggested_content_type', status = item->>'status',
    duplicate_suspected = coalesce((item->>'duplicate_suspected')::boolean, false),
    source_validated = coalesce((item->>'source_validated')::boolean, false),
    link_verified = coalesce((item->>'link_verified')::boolean, false),
    tutorial_evidence_verified = coalesce((item->>'tutorial_evidence_verified')::boolean, false),
    decision_reason = item->>'decision',
    matched_keywords = array(select jsonb_array_elements_text(coalesce(item->'matched_keywords', '[]'::jsonb)))
  from jsonb_array_elements(p_items) item where c.id = (item->>'candidate_id')::uuid;
  return expected;
end;
$$;
revoke all on function public.news_finalize_candidates(jsonb, uuid) from public, anon, authenticated;
grant execute on function public.news_finalize_candidates(jsonb, uuid) to service_role;

create function public.news_ingestion_config(p_now timestamptz)
returns jsonb language plpgsql stable set search_path = pg_catalog as $$
declare result jsonb;
begin
  if current_setting('role', true) is distinct from 'service_role' then
    raise insufficient_privilege using message = 'Service role required';
  end if;
  if p_now is null then raise exception 'Current time is required'; end if;
  select jsonb_build_object(
    'review_required', s.review_required,
    'rules', coalesce((select jsonb_agg(jsonb_build_object('keyword', b.keyword, 'enabled', b.enabled,
                  'content_type', b.content_type)) from public.news_blocked_keywords b), '[]'::jsonb),
    'already_published', (select count(*) from public.published_news p where
      (p.published_at at time zone 'Asia/Shanghai')::date = (p_now at time zone 'Asia/Shanghai')::date),
    'opinions_published', (select count(*) from public.published_news p where p.content_type = 'opinion' and
      (p.published_at at time zone 'Asia/Shanghai')::date = (p_now at time zone 'Asia/Shanghai')::date)
  ) into strict result from public.news_review_settings s where s.id;
  return result;
end;
$$;
revoke all on function public.news_ingestion_config(timestamptz) from public, anon, authenticated;
grant execute on function public.news_ingestion_config(timestamptz) to service_role;

-- Explicit human attestation is separate from ordinary content editing.
create function public.news_review_candidate(p_id uuid, p_revision bigint, p_action text,
  p_reason text, p_tutorial_confirmed boolean, p_duplicate_confirmed boolean)
returns bigint language plpgsql security definer set search_path = pg_catalog as $$
declare candidate public.news_candidates%rowtype; new_revision bigint;
begin
  if current_setting('role', true) is distinct from 'authenticated' or auth.uid() is null
     or not exists (select 1 from public.news_admins a where a.user_id = auth.uid()) then
    raise insufficient_privilege using message = 'Administrator required';
  end if;
  select * into candidate from public.news_candidates where id = p_id for update;
  if not found or candidate.revision is distinct from p_revision then
    raise exception 'Candidate changed or does not exist';
  end if;
  if p_action = 'attest' then
    if candidate.status not in ('new', 'pending', 'selected') or candidate.content_type is null
       or nullif(trim(candidate.title), '') is null or nullif(trim(candidate.summary), '') is null
       or nullif(trim(candidate.source_excerpt), '') is null
       or (candidate.content_type = 'tutorial' and p_tutorial_confirmed is distinct from true)
       or (candidate.duplicate_suspected and p_duplicate_confirmed is distinct from true) then
      raise exception 'Candidate needs further review';
    end if;
    update public.news_candidates set status = 'pending', source_validated = true, link_verified = true,
      tutorial_evidence_verified = (candidate.content_type = 'tutorial' and p_tutorial_confirmed is true),
      duplicate_suspected = false, rejection_reason = null where id = p_id returning revision into new_revision;
  elsif p_action = 'reject' then
    if candidate.status not in ('new', 'pending', 'selected') or nullif(trim(p_reason), '') is null then
      raise exception 'Rejection requires an eligible candidate and a reason';
    end if;
    update public.news_candidates set status = 'rejected', rejection_reason = trim(p_reason)
      where id = p_id returning revision into new_revision;
  elsif p_action = 'restore' then
    if candidate.status <> 'rejected' then raise exception 'Only rejected candidates can be restored'; end if;
    update public.news_candidates set status = 'pending', rejection_reason = null,
      source_validated = false, link_verified = false, tutorial_evidence_verified = false
      where id = p_id returning revision into new_revision;
  else
    raise exception 'Unknown review action';
  end if;
  return new_revision;
end;
$$;
revoke all on function public.news_review_candidate(uuid, bigint, text, text, boolean, boolean) from public, anon, authenticated;
grant execute on function public.news_review_candidate(uuid, bigint, text, text, boolean, boolean) to authenticated;

-- The only client-callable write path to published_news. The singleton settings
-- row serializes mode changes and competing publish operations.
create function public.news_publish_candidates(p_ids uuid[], p_mode text)
returns setof uuid language plpgsql security definer set search_path = pg_catalog as $$
declare
  caller_role text := current_setting('role', true);
  review_on boolean;
  candidate public.news_candidates%rowtype;
  remaining integer := 0;
  opinions integer := 0;
  present_count integer;
begin
  if p_mode not in ('automatic', 'manual') or p_mode is null then
    raise exception 'Invalid publication mode';
  end if;
  if p_mode = 'automatic' then
    if caller_role is distinct from 'service_role' then raise insufficient_privilege using message = 'Service role required'; end if;
  else
    if caller_role is distinct from 'authenticated' or auth.uid() is null or not exists
       (select 1 from public.news_admins a where a.user_id = auth.uid()) then
      raise insufficient_privilege using message = 'Administrator required';
    end if;
  end if;
  if p_ids is null or cardinality(p_ids) < 1 or cardinality(p_ids) > 5
     or array_position(p_ids, null) is not null
     or (select count(distinct x) from unnest(p_ids) as x) <> cardinality(p_ids) then
    raise exception 'Provide one to five distinct candidate IDs';
  end if;
  select review_required into strict review_on from public.news_review_settings where id for update;
  if p_mode = 'automatic' and review_on then raise exception 'Manual review is required'; end if;

  -- Acquire row locks in stable order so overlapping batches cannot race.
  perform 1 from public.news_candidates where id = any(p_ids) order by id for update;
  select count(*) into present_count from public.news_candidates where id = any(p_ids);
  if present_count <> cardinality(p_ids) then raise exception 'Unknown candidate'; end if;

  for candidate in select * from public.news_candidates where id = any(p_ids) order by id loop
    if candidate.status = 'published' and exists
       (select 1 from public.published_news p where p.candidate_id = candidate.id and p.withdrawn_at is null) then
      continue;
    end if;
    if (p_mode = 'automatic' and candidate.status <> 'new')
       or (p_mode = 'manual' and candidate.status not in ('pending', 'selected')) then
      raise exception 'Candidate is not eligible for this publication mode';
    end if;
    if candidate.duplicate_suspected or not candidate.source_validated or not candidate.link_verified
       or candidate.content_type is null or nullif(trim(candidate.title), '') is null
       or nullif(trim(candidate.summary), '') is null or nullif(trim(candidate.source_excerpt), '') is null
       or candidate.link !~* '^https?://[^/@[:space:]]+(/|$|\?)'
       or (candidate.content_type = 'tutorial' and not candidate.tutorial_evidence_verified) then
      raise exception 'Candidate failed publication validation';
    end if;
    if exists (select 1 from public.news_blocked_keywords b where b.enabled
      and (b.content_type is null or b.content_type = candidate.content_type)
      and position(lower(trim(b.keyword)) in lower(concat_ws(E'\n', candidate.title, candidate.summary, candidate.source_excerpt))) > 0) then
      raise exception 'Candidate matches a blocked keyword';
    end if;
    if exists (select 1 from public.published_news p where p.withdrawn_at is null and p.link = candidate.link) then
      raise exception 'Candidate URL already published';
    end if;
    if candidate.content_type = 'technical_update' then
      if candidate.source_published_at is null or candidate.source_published_at > now()
         or candidate.source_published_at < now() - interval '24 hours' then raise exception 'Candidate timestamp is not eligible'; end if;
    else
      if coalesce(candidate.source_updated_at, candidate.source_published_at) is null
         or coalesce(candidate.source_updated_at, candidate.source_published_at) > now()
         or coalesce(candidate.source_updated_at, candidate.source_published_at) < now() - interval '7 days' then
        raise exception 'Candidate timestamp is not eligible';
      end if;
    end if;
    remaining := remaining + 1;
    if candidate.content_type = 'opinion' then opinions := opinions + 1; end if;
  end loop;
  if (select count(*) from public.published_news p where
      (p.published_at at time zone 'Asia/Shanghai')::date = (now() at time zone 'Asia/Shanghai')::date) + remaining > 5 then
    raise exception 'Daily publication limit exceeded';
  end if;
  if (select count(*) from public.published_news p where p.content_type = 'opinion'
      and (p.published_at at time zone 'Asia/Shanghai')::date = (now() at time zone 'Asia/Shanghai')::date) + opinions > 1 then
    raise exception 'Daily opinion limit exceeded';
  end if;
  if exists (select 1 from public.news_candidates where id = any(p_ids) and status <> 'published'
             group by link having count(*) > 1) then raise exception 'Duplicate URLs in batch'; end if;

  for candidate in select * from public.news_candidates where id = any(p_ids) order by id loop
    if candidate.status = 'published' then continue; end if;
    insert into public.published_news (candidate_id, title, summary, detail, link, content_type)
      values (candidate.id, candidate.title, candidate.summary, candidate.detail, candidate.link, candidate.content_type);
    update public.news_candidates set status = 'published', updated_at = now() where id = candidate.id;
    insert into public.news_review_events (actor_id, action, details)
      values (auth.uid(), 'candidate.published', jsonb_build_object('candidate_id', candidate.id, 'mode', p_mode));
  end loop;
  return query select p.id from public.published_news p where p.candidate_id = any(p_ids) and p.withdrawn_at is null order by p.candidate_id;
end;
$$;
revoke all on function public.news_publish_candidates(uuid[], text) from public, anon, authenticated, service_role;
grant execute on function public.news_publish_candidates(uuid[], text) to authenticated, service_role;
