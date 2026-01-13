-- 1. Create the Guestbook Table
create table if not exists guestbook_messages (
  id uuid default gen_random_uuid() primary key,
  user_id text not null, -- Stores the anonymous 'vitemind_user_id'
  content text not null,
  created_at timestamptz default now() not null,
  is_hidden boolean default false -- For moderation
);

-- 2. Create Index on created_at for faster sorting
create index if not exists idx_guestbook_created_at on guestbook_messages(created_at desc);

-- 3. Enable Row Level Security (RLS)
alter table guestbook_messages enable row level security;

-- 4. Create RLS Policies

-- Policy: Allow anyone to view messages that are not hidden
create policy "Public view approved messages"
on guestbook_messages for select
using (is_hidden = false);

-- Policy: Allow anyone to insert messages (Anonymous writes)
-- Note: We rely on the rate limit trigger for protection
create policy "Public insert messages"
on guestbook_messages for insert
with check (true);

-- 5. Rate Limiting Logic (PL/pgSQL)

-- Function: Check if user has exceeded rate limits
-- Limit: Max 5 messages per hour per user_id
create or replace function check_guestbook_rate_limit()
returns trigger as $$
declare
  message_count int;
begin
  -- Count messages from this user in the last hour
  select count(*)
  into message_count
  from guestbook_messages
  where user_id = new.user_id
  and created_at > (now() - interval '1 hour');

  -- Enforce Limit
  if message_count >= 5 then
    raise exception 'Rate limit exceeded: You can only post 5 messages per hour.';
  end if;

  return new;
end;
$$ language plpgsql;

-- Trigger: Run the check before every insert
drop trigger if exists tr_check_guestbook_rate_limit on guestbook_messages;

create trigger tr_check_guestbook_rate_limit
before insert on guestbook_messages
for each row
execute function check_guestbook_rate_limit();

-- 6. Comment for Admin
comment on table guestbook_messages is 'Stores anonymous guestbook entries with rate limiting (5/hr).';
