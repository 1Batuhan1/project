import React, { useEffect, useState, useMemo } from 'react';
import {
  View,
  Text,
  FlatList,
  Image,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  TextInput,
  Alert,
  SafeAreaView,
} from 'react-native';
import { supabase } from '../lib/supabase';
import { useCart } from '../context/CartContext';

export default function ProductListScreen({ navigation }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const { addToCart, totalItemCount, items } = useCart();

  useEffect(() => {
    fetchProducts();
  }, []);

  async function fetchProducts() {
    setLoading(true);
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .eq('active', true)
      .order('category', { ascending: true });

    if (error) {
      setError(error.message);
    } else {
      setProducts(data);
    }
    setLoading(false);
  }

  const filteredProducts = useMemo(() => {
    if (!search.trim()) return products;
    const q = search.trim().toLowerCase();
    return products.filter(
      (p) =>
        p.name?.toLowerCase().includes(q) ||
        p.category?.toLowerCase().includes(q)
    );
  }, [products, search]);

  if (loading) {
    return (
      <SafeAreaView style={styles.center}>
        <ActivityIndicator size="large" />
      </SafeAreaView>
    );
  }

  if (error) {
    return (
      <SafeAreaView style={styles.center}>
        <Text style={styles.errorText}>Ürünler yüklenemedi: {error}</Text>
        <TouchableOpacity onPress={fetchProducts} style={styles.retryBtn}>
          <Text style={styles.retryText}>Tekrar Dene</Text>
        </TouchableOpacity>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Ürünler</Text>
        <TouchableOpacity
          style={styles.cartButton}
          onPress={() => navigation.navigate('Cart')}
        >
          <Text style={styles.cartButtonText}>Sepet ({totalItemCount})</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.searchWrap}>
        <TextInput
          style={styles.searchInput}
          value={search}
          onChangeText={setSearch}
          placeholder="Ürün ara..."
          placeholderTextColor="#999"
          autoCorrect={false}
        />
        {search.length > 0 && (
          <TouchableOpacity style={styles.clearBtn} onPress={() => setSearch('')}>
            <Text style={styles.clearBtnText}>✕</Text>
          </TouchableOpacity>
        )}
      </View>

      <FlatList
        data={filteredProducts}
        keyExtractor={(item) => item.id.toString()}
        style={{ flex: 1 }}
        contentContainerStyle={{ padding: 12 }}
        ListEmptyComponent={
          <Text style={styles.emptySearch}>
            "{search}" ile eşleşen ürün bulunamadı.
          </Text>
        }
        renderItem={({ item }) => {
          const inStock = item.stock_quantity > 0;
          const cartQty = items[item.id]?.quantity || 0;
          const reachedLimit = cartQty >= item.stock_quantity;

          function handleAdd() {
            if (!inStock) return;
            if (reachedLimit) {
              Alert.alert(
                'Stok Sınırı',
                `Bu üründen sepetinize en fazla ${item.stock_quantity} adet ekleyebilirsiniz.`
              );
              return;
            }
            addToCart(item, 1);
          }

          return (
            <View style={[styles.card, !inStock && styles.cardOutOfStock]}>
              {item.image_url ? (
                <Image source={{ uri: item.image_url }} style={styles.image} />
              ) : (
                <View style={[styles.image, styles.imagePlaceholder]} />
              )}
              <View style={{ flex: 1 }}>
                <Text style={styles.productName}>{item.name}</Text>
                <Text style={styles.productCategory}>{item.category}</Text>
                <Text style={styles.productPrice}>
                  {item.price} ₺ / {item.unit}
                </Text>
                {inStock ? (
                  <Text style={styles.stockText}>
                    Stokta: {item.stock_quantity} {item.unit}
                  </Text>
                ) : (
                  <Text style={styles.outOfStockText}>Tükendi</Text>
                )}
              </View>
              <TouchableOpacity
                style={[styles.addButton, !inStock && styles.addButtonDisabled]}
                onPress={handleAdd}
                disabled={!inStock}
              >
                <Text style={styles.addButtonText}>
                  {inStock ? 'Ekle' : 'Tükendi'}
                </Text>
              </TouchableOpacity>
            </View>
          );
        }}
      />

      <TouchableOpacity
        style={styles.adminLink}
        onPress={() => navigation.navigate('AdminLogin')}
      >
        <Text style={styles.adminLinkText}>Yönetici Girişi</Text>
      </TouchableOpacity>
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
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  title: { fontSize: 22, fontWeight: '700' },
  cartButton: {
    backgroundColor: '#1a1a1a',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
  },
  cartButtonText: { color: '#fff', fontWeight: '600' },
  searchWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 16,
    marginTop: 12,
    marginBottom: 4,
    backgroundColor: '#f2f2f2',
    borderRadius: 10,
    paddingHorizontal: 12,
  },
  searchInput: {
    flex: 1,
    paddingVertical: 10,
    fontSize: 15,
  },
  clearBtn: { paddingLeft: 8, paddingVertical: 6 },
  clearBtnText: { color: '#999', fontSize: 15, fontWeight: '700' },
  emptySearch: { textAlign: 'center', color: '#999', marginTop: 40 },
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f7f7f7',
    borderRadius: 10,
    padding: 10,
    marginBottom: 10,
  },
  image: { width: 56, height: 56, borderRadius: 8, marginRight: 12 },
  imagePlaceholder: { backgroundColor: '#ddd' },
  productName: { fontSize: 16, fontWeight: '600' },
  productCategory: { fontSize: 12, color: '#777', marginTop: 2 },
  productPrice: { fontSize: 14, color: '#333', marginTop: 4 },
  stockText: { fontSize: 12, color: '#2f7d3c', marginTop: 3, fontWeight: '600' },
  outOfStockText: { fontSize: 12, color: 'crimson', marginTop: 3, fontWeight: '700' },
  cardOutOfStock: { opacity: 0.6 },
  addButtonDisabled: { backgroundColor: '#bbb' },
  addButton: {
    backgroundColor: '#2f7d3c',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
  },
  addButtonText: { color: '#fff', fontWeight: '600' },
  adminLink: { alignItems: 'center', paddingVertical: 14 },
  adminLinkText: { color: '#999', fontSize: 12 },
  errorText: { color: 'crimson', marginBottom: 12, textAlign: 'center', paddingHorizontal: 20 },
  retryBtn: { backgroundColor: '#1a1a1a', padding: 10, borderRadius: 8 },
  retryText: { color: '#fff' },
});
