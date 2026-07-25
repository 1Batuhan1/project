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
  SafeAreaView,
} from 'react-native';
import { supabase } from '../lib/supabase';
import { useCart } from '../context/CartContext';

export default function OrderFormScreen({ navigation }) {
  const { cartList, clearCart } = useCart();
  const [businessName, setBusinessName] = useState('');
  const [contactPerson, setContactPerson] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [note, setNote] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const validate = () => {
    if (!businessName.trim()) return 'İşletme adı zorunludur.';
    if (!contactPerson.trim()) return 'Yetkili adı zorunludur.';
    const phoneDigits = contactPhone.replace(/\D/g, '');
    if (phoneDigits.length < 10) return 'Geçerli bir cep telefonu numarası girin.';
    return null;
  };

  async function handleSubmit() {
    const validationError = validate();
    if (validationError) {
      Alert.alert('Eksik / Hatalı Bilgi', validationError);
      return;
    }

    setSubmitting(true);

    const total = cartList.reduce(
      (sum, i) => sum + i.quantity * (i.product.price || 0),
      0
    );

    const items = cartList.map((i) => ({
      product_id: i.product.id,
      product_name: i.product.name,
      category: i.product.category,
      quantity: i.quantity,
      unit_price: i.product.price,
    }));

    const { error: rpcError } = await supabase.rpc('create_order', {
      p_business_name: businessName.trim(),
      p_contact_person: contactPerson.trim(),
      p_contact_phone: contactPhone.trim(),
      p_note: note.trim() || null,
      p_total_amount: total,
      p_items: items,
    });

    setSubmitting(false);

    if (rpcError) {
      Alert.alert('Hata', 'Sipariş oluşturulamadı: ' + rpcError.message);
      return;
    }

    clearCart();
    navigation.reset({
      index: 0,
      routes: [{ name: 'OrderConfirmation' }],
    });
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <Text style={styles.title}>Sipariş Bilgileri</Text>
        <Text style={styles.subtitle}>
          Siparişin işlenebilmesi için aşağıdaki bilgileri eksiksiz doldurun.
        </Text>

        <Text style={styles.label}>İşletme İsmi *</Text>
        <TextInput
          style={styles.input}
          value={businessName}
          onChangeText={setBusinessName}
          placeholder="Örn: Yıldız Market"
        />

        <Text style={styles.label}>Yetkili Adı Soyadı *</Text>
        <TextInput
          style={styles.input}
          value={contactPerson}
          onChangeText={setContactPerson}
          placeholder="Örn: Ahmet Yılmaz"
        />

        <Text style={styles.label}>Cep Telefonu *</Text>
        <TextInput
          style={styles.input}
          value={contactPhone}
          onChangeText={setContactPhone}
          placeholder="05XX XXX XX XX"
          keyboardType="phone-pad"
        />

        <Text style={styles.label}>Not (opsiyonel)</Text>
        <TextInput
          style={[styles.input, { height: 80 }]}
          value={note}
          onChangeText={setNote}
          placeholder="Teslimat tercihi, ek bilgi vb."
          multiline
        />

        <TouchableOpacity
          style={styles.submitButton}
          onPress={handleSubmit}
          disabled={submitting}
        >
          {submitting ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.submitButtonText}>Siparişi Gönder</Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  title: { fontSize: 22, fontWeight: '700', marginBottom: 4 },
  subtitle: { fontSize: 13, color: '#777', marginBottom: 20 },
  label: { fontSize: 13, fontWeight: '600', marginTop: 12, marginBottom: 6 },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 15,
  },
  submitButton: {
    backgroundColor: '#2f7d3c',
    padding: 16,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 28,
  },
  submitButtonText: { color: '#fff', fontWeight: '700', fontSize: 15 },
});
