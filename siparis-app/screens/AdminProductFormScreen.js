import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
  Switch,
  SafeAreaView,
} from 'react-native';
import { supabase } from '../lib/supabase';

export default function AdminProductFormScreen({ navigation, route }) {
  const existingProduct = route.params?.product || null;
  const isEditing = !!existingProduct;

  const [name, setName] = useState(existingProduct?.name || '');
  const [category, setCategory] = useState(existingProduct?.category || '');
  const [unit, setUnit] = useState(existingProduct?.unit || 'adet');
  const [price, setPrice] = useState(
    existingProduct ? String(existingProduct.price) : ''
  );
  const [stockQuantity, setStockQuantity] = useState(
    existingProduct ? String(existingProduct.stock_quantity ?? 0) : '0'
  );
  const [imageUrl, setImageUrl] = useState(existingProduct?.image_url || '');
  const [active, setActive] = useState(existingProduct?.active ?? true);
  const [submitting, setSubmitting] = useState(false);

  function validate() {
    if (!name.trim()) return 'Ürün adı zorunludur.';
    if (!category.trim()) return 'Kategori zorunludur.';
    if (!unit.trim()) return 'Birim zorunludur (örn: kg, koli, adet).';
    const priceNum = Number(price.replace(',', '.'));
    if (isNaN(priceNum) || priceNum < 0) return 'Geçerli bir fiyat girin.';
    const stockNum = Number(stockQuantity.replace(',', '.'));
    if (isNaN(stockNum) || stockNum < 0 || !Number.isInteger(stockNum))
      return 'Geçerli bir stok adedi girin (tam sayı, 0 veya üzeri).';
    return null;
  }

  async function handleSave() {
    const validationError = validate();
    if (validationError) {
      Alert.alert('Eksik / Hatalı Bilgi', validationError);
      return;
    }

    setSubmitting(true);
    const payload = {
      name: name.trim(),
      category: category.trim(),
      unit: unit.trim(),
      price: Number(price.replace(',', '.')),
      stock_quantity: Number(stockQuantity.replace(',', '.')),
      image_url: imageUrl.trim() || null,
      active,
    };

    let error;
    if (isEditing) {
      ({ error } = await supabase
        .from('products')
        .update(payload)
        .eq('id', existingProduct.id));
    } else {
      ({ error } = await supabase.from('products').insert(payload));
    }

    setSubmitting(false);

    if (error) {
      Alert.alert('Hata', 'Kaydedilemedi: ' + error.message);
      return;
    }

    navigation.goBack();
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <Text style={styles.title}>
          {isEditing ? 'Ürünü Düzenle' : 'Yeni Ürün Ekle'}
        </Text>

        <Text style={styles.label}>Ürün Adı *</Text>
        <TextInput
          style={styles.input}
          value={name}
          onChangeText={setName}
          placeholder="Örn: Ayçiçek Yağı 5L"
        />

        <Text style={styles.label}>Kategori *</Text>
        <TextInput
          style={styles.input}
          value={category}
          onChangeText={setCategory}
          placeholder="Örn: Yağ, Gıda, Temizlik"
        />

        <Text style={styles.label}>Birim *</Text>
        <TextInput
          style={styles.input}
          value={unit}
          onChangeText={setUnit}
          placeholder="Örn: adet, kg, koli, bidon"
        />

        <Text style={styles.label}>Fiyat (₺) *</Text>
        <TextInput
          style={styles.input}
          value={price}
          onChangeText={setPrice}
          placeholder="Örn: 285.00"
          keyboardType="decimal-pad"
        />

        <Text style={styles.label}>Stok Adedi *</Text>
        <TextInput
          style={styles.input}
          value={stockQuantity}
          onChangeText={setStockQuantity}
          placeholder="Örn: 25"
          keyboardType="number-pad"
        />

        <Text style={styles.label}>Görsel URL (opsiyonel)</Text>
        <TextInput
          style={styles.input}
          value={imageUrl}
          onChangeText={setImageUrl}
          placeholder="https://..."
          autoCapitalize="none"
        />

        <View style={styles.switchRow}>
          <Text style={styles.label}>Ürün Aktif (müşteri listesinde görünsün)</Text>
          <Switch value={active} onValueChange={setActive} />
        </View>

        <TouchableOpacity
          style={styles.submitButton}
          onPress={handleSave}
          disabled={submitting}
        >
          {submitting ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.submitButtonText}>
              {isEditing ? 'Değişiklikleri Kaydet' : 'Ürünü Ekle'}
            </Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity style={styles.cancelButton} onPress={() => navigation.goBack()}>
          <Text style={styles.cancelButtonText}>Vazgeç</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  title: { fontSize: 22, fontWeight: '700', marginBottom: 20 },
  label: { fontSize: 13, fontWeight: '600', marginTop: 12, marginBottom: 6, flexShrink: 1 },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 15,
  },
  switchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  submitButton: {
    backgroundColor: '#2f7d3c',
    padding: 16,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 28,
  },
  submitButtonText: { color: '#fff', fontWeight: '700', fontSize: 15 },
  cancelButton: { alignItems: 'center', padding: 14 },
  cancelButtonText: { color: '#999', fontSize: 13 },
});
