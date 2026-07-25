import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, SafeAreaView } from 'react-native';

export default function OrderConfirmationScreen({ navigation }) {
  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.check}>✓</Text>
      <Text style={styles.title}>Siparişiniz Alındı</Text>
      <Text style={styles.subtitle}>
        Siparişiniz işletme yetkilisine iletildi. En kısa sürede sizinle iletişime
        geçilecektir.
      </Text>
      <TouchableOpacity
        style={styles.button}
        onPress={() => navigation.reset({ index: 0, routes: [{ name: 'ProductList' }] })}
      >
        <Text style={styles.buttonText}>Yeni Sipariş Ver</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 24 },
  check: { fontSize: 60, color: '#2f7d3c', marginBottom: 12 },
  title: { fontSize: 22, fontWeight: '700', marginBottom: 8 },
  subtitle: { fontSize: 14, color: '#777', textAlign: 'center', marginBottom: 28 },
  button: { backgroundColor: '#1a1a1a', paddingHorizontal: 20, paddingVertical: 14, borderRadius: 10 },
  buttonText: { color: '#fff', fontWeight: '700' },
});
