import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Image,
  Alert,
  SafeAreaView,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { supabase } from '../lib/supabase';

export default function AdminProductsScreen({ navigation }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .order('category', { ascending: true })
      .order('name', { ascending: true });
    if (!error) setProducts(data);
    setLoading(false);
  }, []);

  // Ekrana her dönüşte listeyi tazele (yeni ekleme / düzenleme sonrası)
  useFocusEffect(
    useCallback(() => {
      fetchProducts();
    }, [fetchProducts])
  );

  async function toggleActive(product) {
    const { error } = await supabase
      .from('products')
      .update({ active: !product.active })
      .eq('id', product.id);
    if (error) {
      Alert.alert('Hata', error.message);
      return;
    }
    fetchProducts();
  }

  function confirmDelete(product) {
    Alert.alert(
      'Ürünü Sil',
      `"${product.name}" kalıcı olarak silinsin mi?`,
      [
        { text: 'Vazgeç', style: 'cancel' },
        { text: 'Sil', style: 'destructive', onPress: () => deleteProduct(product) },
      ]
    );
  }

  async function deleteProduct(product) {
    const { error } = await supabase.from('products').delete().eq('id', product.id);
    if (error) {
      Alert.alert(
        'Hata',
        'Silinemedi: ' + error.message + '\nBu üründen geçmiş sipariş varsa, silmek yerine "Pasif Yap" seçeneğini kullanabilirsiniz.'
      );
      return;
    }
    fetchProducts();
  }

  if (loading) {
    return (
      <SafeAreaView style={styles.center}>
        <ActivityIndicator size="large" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Ürün Yönetimi</Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => navigation.navigate('AdminProductForm')}
        >
          <Text style={styles.addButtonText}>+ Yeni Ürün</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity
        style={styles.backToOrders}
        onPress={() => navigation.navigate('AdminOrders')}
      >
        <Text style={styles.backToOrdersText}>‹ Siparişlere Dön</Text>
      </TouchableOpacity>

      <FlatList
        data={products}
        keyExtractor={(p) => p.id.toString()}
        style={{ flex: 1 }}
        contentContainerStyle={{ padding: 12 }}
        onRefresh={fetchProducts}
        refreshing={loading}
        ListEmptyComponent={
          <Text style={styles.empty}>Henüz ürün eklenmemiş.</Text>
        }
        renderItem={({ item }) => (
          <View style={[styles.card, !item.active && styles.cardInactive]}>
            {item.image_url ? (
              <Image source={{ uri: item.image_url }} style={styles.image} />
            ) : (
              <View style={[styles.image, styles.imagePlaceholder]} />
            )}
            <View style={{ flex: 1 }}>
              <Text style={styles.name}>{item.name}</Text>
              <Text style={styles.meta}>
                {item.category} • {item.price} ₺ / {item.unit}
              </Text>
              <Text
                style={
                  item.stock_quantity > 0 ? styles.stockOk : styles.stockZero
                }
              >
                Stok: {item.stock_quantity} {item.unit}
              </Text>
              {!item.active && <Text style={styles.inactiveTag}>Pasif</Text>}
            </View>
            <View style={styles.actions}>
              <TouchableOpacity
                style={styles.actionBtn}
                onPress={() =>
                  navigation.navigate('AdminProductForm', { product: item })
                }
              >
                <Text style={styles.actionText}>Düzenle</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.actionBtn} onPress={() => toggleActive(item)}>
                <Text style={styles.actionText}>
                  {item.active ? 'Pasif Yap' : 'Aktif Yap'}
                </Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.actionBtn} onPress={() => confirmDelete(item)}>
                <Text style={[styles.actionText, styles.deleteText]}>Sil</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    paddingBottom: 0,
  },
  title: { fontSize: 22, fontWeight: '700' },
  addButton: {
    backgroundColor: '#2f7d3c',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
  },
  addButtonText: { color: '#fff', fontWeight: '700' },
  backToOrders: { paddingHorizontal: 16, paddingVertical: 10 },
  backToOrdersText: { color: '#777', fontSize: 12 },
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f7f7f7',
    borderRadius: 10,
    padding: 10,
    marginBottom: 10,
  },
  cardInactive: { opacity: 0.5 },
  image: { width: 50, height: 50, borderRadius: 8, marginRight: 10 },
  imagePlaceholder: { backgroundColor: '#ddd' },
  name: { fontSize: 15, fontWeight: '600' },
  meta: { fontSize: 12, color: '#777', marginTop: 2 },
  stockOk: { fontSize: 11, color: '#2f7d3c', fontWeight: '600', marginTop: 2 },
  stockZero: { fontSize: 11, color: 'crimson', fontWeight: '700', marginTop: 2 },
  inactiveTag: { fontSize: 11, color: 'crimson', fontWeight: '700', marginTop: 2 },
  actions: { alignItems: 'flex-end' },
  actionBtn: { paddingVertical: 3 },
  actionText: { color: '#1a1a1a', fontSize: 12, fontWeight: '600' },
  deleteText: { color: 'crimson' },
  empty: { textAlign: 'center', color: '#999', marginTop: 40 },
});
