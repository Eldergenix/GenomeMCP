-- Create user_history table
create table if not exists user_history (
  id uuid default gen_random_uuid() primary key,
  user_id text not null, -- Simple text ID for local user or Auth ID
  type text not null,    -- 'search', 'variant', 'gene', 'pathway'
  query text not null,
  content jsonb not null default '{}',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Index for faster history lookups
create index if not exists idx_user_history_user_id on user_history(user_id);
create index if not exists idx_user_history_created_at on user_history(created_at desc);

-- Create favorites table
create table if not exists favorites (
  id uuid default gen_random_uuid() primary key,
  user_id text not null,
  item_type text not null, -- 'variant', 'gene'
  item_id text not null,   -- Unique business key (e.g. Variant ID or Gene Symbol)
  data jsonb not null default '{}',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  unique(user_id, item_type, item_id) -- Prevent duplicates
);

-- RLS Policies (Open for now, assuming server-side usage or local usage with Service Key if needed, 
-- but ideally should be restricted if used with Supabase Auth)
alter table user_history enable row level security;
alter table favorites enable row level security;

-- Policy to allow all actions for anonymous/service role for now (simplification for CLI tool)
-- In a real multi-user web app, this would be `auth.uid() = user_id`
create policy "Allow all operations for now"
on user_history
for all
using (true)
with check (true);

create policy "Allow all operations for now"
on favorites
for all
using (true)
with check (true);
