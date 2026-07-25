-- ==========================================================
-- SIPARIS APP - Supabase Veritabani Semasi
-- Bu dosyayi Supabase projenizde SQL Editor'e yapistirip
-- calistirin (Supabase Dashboard > SQL Editor > New query).
-- ==========================================================

-- 1) URUNLER TABLOSU
create table products (
  id bigint generated always as identity primary key,
  name text not null,
  category text not null,
  unit text not null default 'adet',        -- kg, koli, adet, litre vb.
  price numeric(10,2) not null default 0,
  stock_quantity integer not null default 0,
  image_url text,
  active boolean not null default true,
  created_at timestamptz not null default now()
);

-- 2) SIPARISLER TABLOSU
create table orders (
  id bigint generated always as identity primary key,
  business_name text not null,
  contact_person text not null,
  contact_phone text not null,
  note text,
  total_amount numeric(10,2) not null default 0,
  status text not null default 'yeni',       -- yeni, hazirlaniyor, tamamlandi, iptal
  created_at timestamptz not null default now()
);

-- 3) SIPARIS KALEMLERI (her siparisteki urun satirlari)
create table order_items (
  id bigint generated always as identity primary key,
  order_id bigint not null references orders(id) on delete cascade,
  product_id bigint references products(id),
  product_name text not null,
  category text,
  quantity numeric(10,2) not null default 1,
  unit_price numeric(10,2) not null default 0,
  created_at timestamptz not null default now()
);

-- ==========================================================
-- ROW LEVEL SECURITY (RLS) - erisim kurallari
-- ==========================================================

alter table products enable row level security;
alter table orders enable row level security;
alter table order_items enable row level security;

-- Herkes (anon dahil) aktif urunleri gorebilir
create policy "Herkes urunleri okuyabilir"
  on products for select
  using (active = true);

-- Admin, pasif urunler dahil TUM urunleri gorebilir (urun yonetimi ekrani icin)
create policy "Admin tum urunleri okuyabilir"
  on products for select
  using (auth.role() = 'authenticated');

-- Herkes (anon dahil) siparis olusturabilir (musteri formu)
-- NOT: Dogrudan tabloya degil, asagidaki create_order() fonksiyonu
-- uzerinden siparis olusturulur (guvenlik icin, "security definer"
-- kullanan fonksiyon RLS'i kendi yetkisiyle asar).

-- Sadece giris yapmis (admin) kullanicilar siparisleri okuyabilir
create policy "Sadece admin siparisleri okuyabilir"
  on orders for select
  using (auth.role() = 'authenticated');

create policy "Sadece admin siparis kalemlerini okuyabilir"
  on order_items for select
  using (auth.role() = 'authenticated');

-- Sadece admin siparis durumunu guncelleyebilir
create policy "Sadece admin siparis guncelleyebilir"
  on orders for update
  using (auth.role() = 'authenticated');

-- Sadece admin urun ekleyebilir / duzenleyebilir / silebilir
-- (Musteri tarafi sadece "select" politikasiyla aktif urunleri gorur.)
create policy "Sadece admin urun ekleyebilir"
  on products for insert
  with check (auth.role() = 'authenticated');

create policy "Sadece admin urun guncelleyebilir"
  on products for update
  using (auth.role() = 'authenticated');

create policy "Sadece admin urun silebilir"
  on products for delete
  using (auth.role() = 'authenticated');

-- ==========================================================
-- ORNEK URUN VERISI (istege bagli - test icin)
-- ==========================================================
insert into products (name, category, unit, price, stock_quantity, active) values
  ('Ayciceği Yağı 5L', 'Yağ', 'bidon', 285.00, 40, true),
  ('Toz Şeker 50kg', 'Gıda', 'çuval', 1450.00, 15, true),
  ('Makarna 500g Koli (20 adet)', 'Gıda', 'koli', 340.00, 25, true),
  ('Bulaşık Deterjanı 5L', 'Temizlik', 'bidon', 210.00, 0, true),
  ('Çay 1kg', 'Gıda', 'paket', 165.00, 60, true);

-- ==========================================================
-- SIPARIS OLUSTURMA FONKSIYONU
-- Musteri formu, guvenlik nedeniyle siparisi dogrudan tabloya
-- degil, bu fonksiyon uzerinden olusturur.
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

-- ==========================================================
-- ADMIN KULLANICISI OLUSTURMA
-- SQL ile degil, Supabase Dashboard > Authentication > Users
-- kismindan "Add user" ile bir e-posta/sifre olusturun.
-- Bu bilgilerle uygulamadaki "Yonetici Girisi" ekranindan giris
-- yapilabilir.
-- ==========================================================
