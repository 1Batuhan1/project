import React from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
} from 'react-native';
import { useCart } from '../context/CartContext';

export default function CartScreen({ navigation }) {
  const { cartList, updateQuantity, removeFromCart } = useCart();

  const total = cartList.reduce(
    (sum, i) => sum + i.quantity * (i.product.price || 0),
    0
  );

  if (cartList.length === 0) {
    return (
      <SafeAreaView style={styles.center}>
        <Text style={styles.emptyText}>Sepetiniz boş.</Text>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>Ürünlere Dön</Text>
        </TouchableOpacity>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>Sepetim</Text>
      <FlatList
        data={cartList}
        keyExtractor={(i) => i.product.id.toString()}
        style={{ flex: 1 }}
        contentContainerStyle={{ padding: 12 }}
        renderItem={({ item }) => {
          const atStockLimit = item.quantity >= item.product.stock_quantity;
          return (
          <View style={styles.row}>
            <View style={{ flex: 1 }}>
              <Text style={styles.name}>{item.product.name}</Text>
              <Text style={styles.unit}>
                {item.product.price} ₺ / {item.product.unit}
              </Text>
              {atStockLimit && (
                <Text style={styles.stockLimit}>
                  Stok sınırına ulaşıldı ({item.product.stock_quantity} adet)
                </Text>
              )}
            </View>
            <View style={styles.qtyControls}>
              <TouchableOpacity
                style={styles.qtyBtn}
                onPress={() =>
                  updateQuantity(item.product.id, item.quantity - 1)
                }
              >
                <Text style={styles.qtyBtnText}>-</Text>
              </TouchableOpacity>
              <Text style={styles.qtyText}>{item.quantity}</Text>
              <TouchableOpacity
                style={[styles.qtyBtn, atStockLimit && styles.qtyBtnDisabled]}
                disabled={atStockLimit}
                onPress={() =>
                  updateQuantity(item.product.id, item.quantity + 1)
                }
              >
                <Text style={styles.qtyBtnText}>+</Text>
              </TouchableOpacity>
            </View>
            <TouchableOpacity onPress={() => removeFromCart(item.product.id)}>
              <Text style={styles.remove}>Sil</Text>
            </TouchableOpacity>
          </View>
          );
        }}
      />
      <View style={styles.footer}>
        <Text style={styles.totalText}>Toplam: {total.toFixed(2)} ₺</Text>
        <TouchableOpacity
          style={styles.continueButton}
          onPress={() => navigation.navigate('OrderForm')}
        >
          <Text style={styles.continueButtonText}>Siparişi Tamamla</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  title: { fontSize: 22, fontWeight: '700', padding: 16 },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f7f7f7',
    borderRadius: 10,
    padding: 10,
    marginBottom: 10,
  },
  name: { fontSize: 15, fontWeight: '600' },
  unit: { fontSize: 12, color: '#777', marginTop: 2 },
  qtyControls: { flexDirection: 'row', alignItems: 'center', marginHorizontal: 10 },
  qtyBtn: {
    width: 28,
    height: 28,
    borderRadius: 6,
    backgroundColor: '#ddd',
    alignItems: 'center',
    justifyContent: 'center',
  },
  qtyBtnText: { fontSize: 16, fontWeight: '700' },
  qtyBtnDisabled: { backgroundColor: '#f0f0f0', opacity: 0.5 },
  stockLimit: { fontSize: 11, color: 'crimson', marginTop: 3 },
  qtyText: { marginHorizontal: 10, fontSize: 15, fontWeight: '600' },
  remove: { color: 'crimson', fontSize: 12 },
  footer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  totalText: { fontSize: 18, fontWeight: '700', marginBottom: 10 },
  continueButton: {
    backgroundColor: '#2f7d3c',
    padding: 14,
    borderRadius: 10,
    alignItems: 'center',
  },
  continueButtonText: { color: '#fff', fontWeight: '700', fontSize: 15 },
  emptyText: { fontSize: 16, color: '#777', marginBottom: 16 },
  backButton: { backgroundColor: '#1a1a1a', padding: 12, borderRadius: 8 },
  backButtonText: { color: '#fff' },
});
