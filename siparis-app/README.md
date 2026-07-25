# Sipariş Uygulaması

Firma ürünlerinin listelendiği, müşterinin sepete ekleyip işletme bilgileriyle
sipariş verdiği, sipariş verilerinin de yönetici paneline düştüğü tek kod
tabanlı (Expo / React Native) mobil uygulama. Aynı `.js` kod tabanı hem
Android hem iOS'ta çalışır.

## Ekranlar
- **Ürünler** — aktif ürün listesi, sepete ekleme
- **Sepet** — miktar güncelleme, silme, toplam tutar
- **Sipariş Formu** — işletme ismi, yetkili adı, cep telefonu (zorunlu), not
- **Yönetici Girişi** — e-posta/şifre ile giriş (Supabase Auth)
- **Yönetici Paneli — Siparişler** — gelen siparişler; işletme adına göre arama, ürün
  kategorisine göre filtreleme, miktar ve ürün bazlı detay
- **Yönetici Paneli — Ürün Yönetimi** — ürün ekleme, düzenleme, aktif/pasif
  yapma, silme (uygulamadan çıkmadan, doğrudan panelden)

## 1) Gereksinimler
- Node.js (LTS) yüklü olmalı
- Telefonda **Expo Go** uygulaması (Android: Play Store, iOS: App Store)
- Ücretsiz bir [Supabase](https://supabase.com) hesabı

## 2) Supabase Kurulumu (bulut veritabanı)
1. supabase.com üzerinde ücretsiz yeni proje oluşturun.
2. Proje içinde **SQL Editor**'ü açın, bu klasördeki `supabase-schema.sql`
   dosyasının tamamını yapıştırıp çalıştırın. Bu, `products`, `orders`,
   `order_items` tablolarını ve gerekli erişim kurallarını (RLS) oluşturur,
   ayrıca birkaç örnek ürün ekler.
3. **Authentication > Users** kısmından yönetici için bir e-posta/şifre
   kullanıcısı oluşturun (bu bilgilerle uygulamadaki "Yönetici Girişi"nden
   giriş yapılacak).
4. **Project Settings > API** kısmından `Project URL` ve `anon public` key
   değerlerini kopyalayın.

## 3) Uygulamayı Çalıştırma
```bash
cd siparis-app
npm install
```

`app.json` dosyasını açıp `extra` kısmındaki şu iki değeri Supabase'ten
aldığınız bilgilerle değiştirin:
```json
"extra": {
  "supabaseUrl": "https://xxxx.supabase.co",
  "supabaseAnonKey": "xxxxxxxx..."
}
```

Sonra başlatın:
```bash
npx expo start
```
Terminalde çıkan QR kodu telefonunuzda Expo Go uygulamasıyla okutun; uygulama
hem Android hem iOS cihazda anında açılır.

## 4) Gerçek Uygulama Olarak Yayınlama (App Store / Play Store)
Geliştirme bittiğinde mağazalara yüklenebilir gerçek `.apk` / `.ipa`
dosyaları için [EAS Build](https://docs.expo.dev/build/introduction/)
kullanılır:
```bash
npm install -g eas-cli
eas login
eas build:configure
eas build --platform android
eas build --platform ios
```
iOS derlemesi için ücretli bir Apple Developer hesabı (yıllık $99) gerekir.
Android için Google Play Developer hesabı tek seferlik ücretlidir (~$25).

## 5) Ürünleri Yönetme
Ürünler artık uygulama içinden yönetilebiliyor: Yönetici Girişi yapıp
**Siparişler** ekranındaki **"Ürün Yönetimi"** sekmesine geçin. Buradan:
- **+ Yeni Ürün** ile ürün ekleyebilir,
- Bir ürünün **Düzenle** butonuyla bilgilerini güncelleyebilir,
- **Pasif Yap / Aktif Yap** ile ürünü müşteri listesinden gizleyip
  gösterebilir (geçmiş siparişlerde adı geçen ürünü silmek yerine bu
  önerilir),
- **Sil** ile ürünü kalıcı olarak kaldırabilirsiniz (bir üründen geçmiş
  sipariş varsa veritabanı bunu engeller; bu durumda "Pasif Yap" kullanın).

İstenirse ürünler yine Supabase Dashboard'daki **Table Editor > products**
kısmından da doğrudan düzenlenebilir.

## Klasör Yapısı
```
siparis-app/
 App.js                     # Navigasyon ve ana giriş noktası
 app.json                   # Expo ayarları + Supabase anahtarları
 supabase-schema.sql        # Veritabanı tabloları ve güvenlik kuralları
 context/
│   └── CartContext.js         # Sepet state yönetimi
 lib/
│   └── supabase.js            # Supabase bağlantı istemcisi
└── screens/
     ProductListScreen.js
     CartScreen.js
     OrderFormScreen.js
     OrderConfirmationScreen.js
     AdminLoginScreen.js
     AdminOrdersScreen.js
     AdminProductsScreen.js
    └── AdminProductFormScreen.js
```

## Sonraki Adımlar (opsiyonel geliştirmeler)
- Sipariş durumunu admin panelinden değiştirme (yeni → hazırlanıyor → tamamlandı)
- Push bildirimi: yeni sipariş geldiğinde yöneticiye anlık bildirim
- Sipariş geçmişi filtreleme (tarih aralığı, durum)
- Ürün fotoğrafı doğrudan telefondan yükleme (şu an sadece görsel URL'i giriliyor)
