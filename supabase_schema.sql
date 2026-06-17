-- Create the accounts table
CREATE TABLE accounts (
  card_number TEXT PRIMARY KEY,
  pin TEXT NOT NULL,
  name TEXT NOT NULL,
  balance NUMERIC NOT NULL DEFAULT 0.00,
  failed_attempts INTEGER NOT NULL DEFAULT 0,
  is_blocked BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert test accounts (N = 10)
INSERT INTO accounts (card_number, pin, name, balance) VALUES
  ('11112222', '1234', 'John Doe',        50000.00),
  ('22223333', '2345', 'Jane Smith',       75000.50),
  ('33334444', '3456', 'Arjun Patel',     120000.75),
  ('44445555', '4567', 'Priya Nair',       30000.00),
  ('55556666', '5678', 'Rahul Sharma',     85000.25),
  ('66667777', '6789', 'Meera Iyer',       15000.00),
  ('77778888', '7890', 'Vikram Das',      200000.00),
  ('88889999', '8901', 'Anjali Reddy',     62500.00),
  ('99990000', '9012', 'Kiran Mehta',      47800.50),
  ('10001001', '0123', 'Suresh Kumar',    100000.00);

-- Create the transactions table
CREATE TABLE transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  card_number TEXT REFERENCES accounts(card_number),
  amount NUMERIC NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('WITHDRAWAL', 'DEPOSIT')),
  image_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create a storage bucket for security captures
-- Note: Replace 'true' with proper Row Level Security (RLS) if in production
insert into storage.buckets (id, name, public)
values ('security_captures', 'security_captures', true);

-- Enable RLS for buckets (Allow public access for this simple demo)
CREATE POLICY "Public Access" 
ON storage.objects FOR ALL 
USING ( bucket_id = 'security_captures' );
