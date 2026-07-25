import React, { useEffect, useState, useMemo } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  TextInput,
  SafeAreaView,
} from 'react-native';
import { supabase } from '../lib/supabase';

export default function AdminOrdersScreen({ navigation }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('Tümü');

  useEffect(() => {
    fetchOrders();
  }, []);

  async function fetchOrders() {
    setLoading(true);
    // Siparişleri, içindeki ürün kalemleriyle birlikte çeker.
    const { data, error } = await supabase
      .from('orders')
      .select('*, order_items(*)')
      .order('created_at', { ascending: false });

    if (!error) setOrders(data);
    setLoading(false);
  }

  async function handleLogout() {
    await supabase.auth.signOut();
    navigation.reset({ index: 0, routes: [{ name: 'ProductList' }] });
  }

  const categories = useMemo(() => {
    const set = new Set(['Tümü']);
    orders.forEach((o) => o.order_items?.forEach((i) => set.add(i.category)));
    return Array.from(set);
  }, [orders]);

  const filteredOrders = useMemo(() => {
    return orders.filter((o) => {
      const matchesSearch =
        !search.trim() ||
        o.business_name?.toLowerCase().includes(search.trim().toLowerCase());
      const matchesCategory =
        categoryFilter === 'Tümü' ||
        o.order_items?.some((i) => i.category === categoryFilter);
      return matchesSearch && matchesCategory;
    });
  }, [orders, search, categoryFilter]);

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
        <Text style={styles.title}>Gelen Siparişler</Text>
        <TouchableOpacity onPress={handleLogout}>
          <Text style={styles.logout}>Çıkış</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.tabRow}>
        <View style={[styles.tabBtn, styles.tabBtnActive]}>
          <Text style={styles.tabTextActive}>Siparişler</Text>
        </View>
        <TouchableOpacity
          style={styles.tabBtn}
          onPress={() => navigation.navigate('AdminProducts')}
        >
          <Text style={styles.tabText}>Ürün Yönetimi</Text>
        </TouchableOpacity>
      </View>

      <TextInput
        style={styles.search}
        placeholder="İşletme ismine göre ara..."
        value={search}
        onChangeText={setSearch}
      />

      <FlatList
        horizontal
        data={categories}
        keyExtractor={(c) => c}
        style={{ flexGrow: 0, marginBottom: 8 }}
        contentContainerStyle={{ paddingHorizontal: 12 }}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[styles.chip, categoryFilter === item && styles.chipActive]}
            onPress={() => setCategoryFilter(item)}
          >
            <Text
              style={[
                styles.chipText,
                categoryFilter === item && styles.chipTextActive,
              ]}
            >
              {item}
            </Text>
          </TouchableOpacity>
        )}
      />

      <FlatList
        data={filteredOrders}
        keyExtractor={(o) => o.id.toString()}
        style={{ flex: 1 }}
        contentContainerStyle={{ padding: 12 }}
        onRefresh={fetchOrders}
        refreshing={loading}
        ListEmptyComponent={
          <Text style={styles.empty}>Kriterlere uyan sipariş bulunamadı.</Text>
        }
        renderItem={({ item }) => (
          <View style={styles.orderCard}>
            <View style={styles.orderHeader}>
              <Text style={styles.businessName}>{item.business_name}</Text>
              <Text style={styles.status}>{item.status}</Text>
            </View>
            <Text style={styles.contact}>
              {item.contact_person} • {item.contact_phone}
            </Text>
            <Text style={styles.date}>
              {new Date(item.created_at).toLocaleString('tr-TR')}
            </Text>

            {item.order_items?.map((line) => (
              <View key={line.id} style={styles.itemRow}>
                <Text style={styles.itemName}>{line.product_name}</Text>
                <Text style={styles.itemCategory}>{line.category}</Text>
                <Text style={styles.itemQty}>x{line.quantity}</Text>
              </View>
            ))}

            {item.note ? <Text style={styles.note}>Not: {item.note}</Text> : null}
            <Text style={styles.total}>Toplam: {item.total_amount} ₺</Text>

            <TouchableOpacity
              style={styles.invoiceButton}
              onPress={() => navigation.navigate('AdminInvoice', { order: item })}
            >
              <Text style={styles.invoiceButtonText}>Fatura Görüntüle / Yazdır</Text>
            </TouchableOpacity>
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
  },
  title: { fontSize: 22, fontWeight: '700' },
  logout: { color: 'crimson', fontWeight: '600' },
  tabRow: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  tabBtn: {
    paddingVertical: 10,
    marginRight: 20,
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  tabBtnActive: { borderBottomColor: '#1a1a1a' },
  tabText: { color: '#999', fontWeight: '600', fontSize: 13 },
  tabTextActive: { color: '#1a1a1a', fontWeight: '700', fontSize: 13 },
  search: {
    marginHorizontal: 16,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 10,
    marginBottom: 10,
  },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    backgroundColor: '#eee',
    borderRadius: 20,
    marginRight: 8,
  },
  chipActive: { backgroundColor: '#1a1a1a' },
  chipText: { color: '#333', fontSize: 12, fontWeight: '600' },
  chipTextActive: { color: '#fff' },
  orderCard: {
    backgroundColor: '#f7f7f7',
    borderRadius: 10,
    padding: 14,
    marginBottom: 12,
  },
  orderHeader: { flexDirection: 'row', justifyContent: 'space-between' },
  businessName: { fontSize: 16, fontWeight: '700' },
  status: { fontSize: 12, color: '#2f7d3c', fontWeight: '700', textTransform: 'uppercase' },
  contact: { fontSize: 13, color: '#555', marginTop: 2 },
  date: { fontSize: 11, color: '#999', marginTop: 2, marginBottom: 8 },
  itemRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
    borderTopWidth: 1,
    borderTopColor: '#e5e5e5',
  },
  itemName: { flex: 1, fontSize: 13 },
  itemCategory: { fontSize: 11, color: '#888', marginHorizontal: 8 },
  itemQty: { fontSize: 13, fontWeight: '700' },
  note: { fontSize: 12, color: '#555', marginTop: 8, fontStyle: 'italic' },
  total: { fontSize: 14, fontWeight: '700', marginTop: 10, textAlign: 'right' },
  invoiceButton: {
    backgroundColor: '#1a1a1a',
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  invoiceButtonText: { color: '#fff', fontWeight: '600', fontSize: 13 },
  empty: { textAlign: 'center', color: '#999', marginTop: 40 },
});
