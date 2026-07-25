-- ==========================================================
-- STOK TAKIBI EKLEME
-- Bu SQL'i Supabase SQL Editor'de calistirin.
-- ==========================================================

-- 1) Urunlere stok adedi sutunu ekle
alter table products
  add column if not exists stock_quantity integer not null default 0;

-- 2) create_order fonksiyonunu, siparis verilince stok dusecek ve
--    yetersiz stokta siparisi reddedecek sekilde guncelle.
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
  v_item jsonb;
  v_product_id bigint;
  v_quantity numeric;
  v_available integer;
  v_product_name text;
begin
  -- Once tum urunler icin stok kontrolu yap ve dus (satir kilidi ile,
  -- ayni anda gelen siparislerde stogun eksiye dusmesini engeller)
  for v_item in select * from jsonb_array_elements(p_items)
  loop
    v_product_id := (v_item->>'product_id')::bigint;
    v_quantity := (v_item->>'quantity')::numeric;

    select stock_quantity, name into v_available, v_product_name
    from products
    where id = v_product_id
    for update;

    if v_available is null then
      raise exception 'Ürün bulunamadı (id: %)', v_product_id;
    end if;

    if v_available < v_quantity then
      raise exception '"%" için yeterli stok kalmadı (kalan: %)', v_product_name, v_available;
    end if;

    update products
    set stock_quantity = stock_quantity - v_quantity
    where id = v_product_id;
  end loop;

  insert into orders (business_name, contact_person, contact_phone, note, total_amount, status)
  values (p_business_name, p_contact_person, p_contact_phone, p_note, p_total_amount, 'yeni')
  returning id into new_order_id;

  insert into order_items (order_id, product_id, product_name, category, quantity, unit_price)
  select
    new_order_id,
    (elem->>'product_id')::bigint,
    elem->>'product_name',
    elem->>'category',
    (elem->>'quantity')::numeric,
    (elem->>'unit_price')::numeric
  from jsonb_array_elements(p_items) as elem;

  return new_order_id;
end;
$$;

grant execute on function create_order(text, text, text, text, numeric, jsonb) to anon, authenticated;
