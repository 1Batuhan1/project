import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';

import { CartProvider } from './context/CartContext';
import ProductListScreen from './screens/ProductListScreen';
import CartScreen from './screens/CartScreen';
import OrderFormScreen from './screens/OrderFormScreen';
import OrderConfirmationScreen from './screens/OrderConfirmationScreen';
import AdminLoginScreen from './screens/AdminLoginScreen';
import AdminOrdersScreen from './screens/AdminOrdersScreen';
import AdminProductsScreen from './screens/AdminProductsScreen';
import AdminProductFormScreen from './screens/AdminProductFormScreen';
import AdminInvoiceScreen from './screens/AdminInvoiceScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <CartProvider>
      <NavigationContainer>
        <StatusBar style="dark" />
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          <Stack.Screen name="ProductList" component={ProductListScreen} />
          <Stack.Screen name="Cart" component={CartScreen} />
          <Stack.Screen name="OrderForm" component={OrderFormScreen} />
          <Stack.Screen name="OrderConfirmation" component={OrderConfirmationScreen} />
          <Stack.Screen name="AdminLogin" component={AdminLoginScreen} />
          <Stack.Screen name="AdminOrders" component={AdminOrdersScreen} />
          <Stack.Screen name="AdminProducts" component={AdminProductsScreen} />
          <Stack.Screen name="AdminProductForm" component={AdminProductFormScreen} />
          <Stack.Screen name="AdminInvoice" component={AdminInvoiceScreen} />
        </Stack.Navigator>
      </NavigationContainer>
    </CartProvider>
  );
}
