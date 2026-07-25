-- ==========================================================
-- SIPARIS OLUSTURMA FONKSIYONU (guvenli, RLS sorununu cozer)
-- Bu SQL'i Supabase SQL Editor'de calistirin.
-- ==========================================================

create or replace function create_order(
  p_business_name text,
  p_contact_person text,
  p_contact_phone text,
  p_note text,
  p_total_amount numeric,
  p_items jsonb
) returns bigint
language plpgsql
security definer
set search_path = public
as $$
declare
  new_order_id bigint;
begin
  insert into orders (business_name, contact_person, contact_phone, note, total_amount, status)
  values (p_business_name, p_contact_person, p_contact_phone, p_note, p_total_amount, 'yeni')
  returning id into new_order_id;

  insert into order_items (order_id, product_id, product_name, category, quantity, unit_price)
  select
    new_order_id,
    (item->>'product_id')::bigint,
    item->>'product_name',
    item->>'category',
    (item->>'quantity')::numeric,
    (item->>'unit_price')::numeric
  from jsonb_array_elements(p_items) as item;

  return new_order_id;
end;
$$;

-- Herkes (musteriler dahil) bu fonksiyonu cagirabilsin
grant execute on function create_order(text, text, text, text, numeric, jsonb) to anon, authenticated;

-- Artik dogrudan tabloya INSERT izni gerekmiyor (fonksiyon guvenli sekilde
-- kendi yetkisiyle ekliyor), bu yuzden eski genel-erisimli insert
-- politikalarini kaldirip erisimi daraltiyoruz.
drop policy if exists "Herkes siparis olusturabilir" on orders;
drop policy if exists "Herkes siparis kalemi olusturabilir" on order_items;
