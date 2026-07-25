import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
  SafeAreaView,
} from 'react-native';
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';

function buildInvoiceHtml(order) {
  const items = order.order_items || [];

  const rows = items
    .map((item) => {
      const lineTotal = (item.quantity * item.unit_price).toFixed(2);
      return `
        <tr>
          <td>${item.product_name}</td>
          <td class="center">${item.quantity}</td>
          <td class="right">${Number(item.unit_price).toFixed(2)} ₺</td>
          <td class="right">${item.quantity} x ${Number(item.unit_price).toFixed(2)} ₺ = <strong>${lineTotal} ₺</strong></td>
        </tr>
      `;
    })
    .join('');

  const dateStr = new Date(order.created_at).toLocaleString('tr-TR');

  return `
    <html>
      <head>
        <meta charset="utf-8" />
        <style>
          body { font-family: -apple-system, Helvetica, Arial, sans-serif; padding: 24px; color: #1a1a1a; }
          h1 { font-size: 20px; margin-bottom: 4px; }
          .meta { color: #555; font-size: 13px; margin-bottom: 20px; }
          table { width: 100%; border-collapse: collapse; margin-top: 12px; }
          th { text-align: left; font-size: 12px; color: #777; border-bottom: 2px solid #ddd; padding: 8px 6px; }
          td { padding: 10px 6px; border-bottom: 1px solid #eee; font-size: 13px; }
          .center { text-align: center; }
          .right { text-align: right; }
          .total-row td { border-top: 2px solid #1a1a1a; border-bottom: none; font-size: 16px; font-weight: 700; padding-top: 14px; }
          .signature { margin-top: 70px; display: flex; justify-content: space-between; }
          .sig-box { width: 45%; }
          .sig-line { border-top: 1px solid #1a1a1a; margin-top: 50px; padding-top: 6px; font-size: 12px; color: #555; }
          .note { margin-top: 20px; font-size: 12px; color: #555; font-style: italic; }
        </style>
      </head>
      <body>
        <h1>Sipariş Faturası</h1>
        <div class="meta">
          <strong>İşletme:</strong> ${order.business_name}<br/>
          <strong>Yetkili:</strong> ${order.contact_person} &nbsp;•&nbsp; <strong>Tel:</strong> ${order.contact_phone}<br/>
          <strong>Sipariş No:</strong> #${order.id} &nbsp;•&nbsp; <strong>Tarih:</strong> ${dateStr}
        </div>

        <table>
          <thead>
            <tr>
              <th>Ürün</th>
              <th class="center">Adet</th>
              <th class="right">Birim Fiyat</th>
              <th class="right">Tutar</th>
            </tr>
          </thead>
          <tbody>
            ${rows}
            <tr class="total-row">
              <td colspan="3" class="right">Genel Toplam</td>
              <td class="right">${Number(order.total_amount).toFixed(2)} ₺</td>
            </tr>
          </tbody>
        </table>

        ${order.note ? `<div class="note">Not: ${order.note}</div>` : ''}

        <div class="signature">
          <div class="sig-box">
            <div class="sig-line">Teslim Eden (İşletme Yetkilisi)</div>
          </div>
          <div class="sig-box">
            <div class="sig-line">Teslim Alan (Müşteri İmzası)</div>
          </div>
        </div>
      </body>
    </html>
  `;
}

export default function AdminInvoiceScreen({ route }) {
  const { order } = route.params;
  const [working, setWorking] = useState(false);

  async function handlePrintOrShare() {
    setWorking(true);
    try {
      const html = buildInvoiceHtml(order);
      const { uri } = await Print.printToFileAsync({ html });

      const canShare = await Sharing.isAvailableAsync();
      if (canShare) {
        await Sharing.shareAsync(uri, {
          mimeType: 'application/pdf',
          dialogTitle: `Fatura - ${order.business_name}`,
        });
      } else {
        // Paylaşım desteklenmiyorsa doğrudan yazdırma diyaloğunu aç
        await Print.printAsync({ uri });
      }
    } catch (err) {
      Alert.alert('Hata', 'Fatura oluşturulamadı: ' + err.message);
    } finally {
      setWorking(false);
    }
  }

  async function handleDirectPrint() {
    setWorking(true);
    try {
      const html = buildInvoiceHtml(order);
      await Print.printAsync({ html });
    } catch (err) {
      Alert.alert('Hata', 'Yazdırma başlatılamadı: ' + err.message);
    } finally {
      setWorking(false);
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <Text style={styles.title}>Fatura Önizleme</Text>
        <Text style={styles.subtitle}>
          #{order.id} • {order.business_name}
        </Text>

        <View style={styles.card}>
          {(order.order_items || []).map((item) => (
            <View key={item.id} style={styles.itemRow}>
              <Text style={styles.itemName}>{item.product_name}</Text>
              <Text style={styles.itemDetail}>
                {item.quantity} x {Number(item.unit_price).toFixed(2)} ₺ ={' '}
                <Text style={styles.itemBold}>
                  {(item.quantity * item.unit_price).toFixed(2)} ₺
                </Text>
              </Text>
            </View>
          ))}
          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>Genel Toplam</Text>
            <Text style={styles.totalValue}>
              {Number(order.total_amount).toFixed(2)} ₺
            </Text>
          </View>
        </View>

        <Text style={styles.hint}>
          Aşağıdaki butonla PDF olarak paylaşabilir, yazıcıya gönderebilir veya
          telefona kaydedebilirsiniz. Belgenin altında müşteri imzası için ayrılmış
          bir bölüm bulunuyor.
        </Text>

        <TouchableOpacity
          style={styles.primaryButton}
          onPress={handlePrintOrShare}
          disabled={working}
        >
          {working ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.primaryButtonText}>PDF Paylaş / Kaydet</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.secondaryButton}
          onPress={handleDirectPrint}
          disabled={working}
        >
          <Text style={styles.secondaryButtonText}>Doğrudan Yazdır</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  title: { fontSize: 22, fontWeight: '700' },
  subtitle: { fontSize: 13, color: '#777', marginBottom: 16 },
  card: {
    backgroundColor: '#f7f7f7',
    borderRadius: 10,
    padding: 14,
    marginBottom: 16,
  },
  itemRow: {
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e5e5',
  },
  itemName: { fontSize: 14, fontWeight: '600' },
  itemDetail: { fontSize: 13, color: '#555', marginTop: 2 },
  itemBold: { fontWeight: '700', color: '#1a1a1a' },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 12,
    marginTop: 4,
  },
  totalLabel: { fontSize: 15, fontWeight: '700' },
  totalValue: { fontSize: 15, fontWeight: '700' },
  hint: { fontSize: 12, color: '#777', marginBottom: 20 },
  primaryButton: {
    backgroundColor: '#2f7d3c',
    padding: 16,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 10,
  },
  primaryButtonText: { color: '#fff', fontWeight: '700', fontSize: 15 },
  secondaryButton: {
    backgroundColor: '#eee',
    padding: 14,
    borderRadius: 10,
    alignItems: 'center',
  },
  secondaryButtonText: { color: '#333', fontWeight: '600', fontSize: 14 },
});
