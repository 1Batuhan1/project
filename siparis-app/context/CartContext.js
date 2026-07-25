import React, { createContext, useContext, useState, useMemo } from 'react';

const CartContext = createContext(null);

export function CartProvider({ children }) {
  // items: { [productId]: { product, quantity } }
  const [items, setItems] = useState({});

  const addToCart = (product, quantity = 1) => {
    setItems((prev) => {
      const existing = prev[product.id];
      const newQty = (existing?.quantity || 0) + quantity;
      return { ...prev, [product.id]: { product, quantity: newQty } };
    });
  };

  const updateQuantity = (productId, quantity) => {
    setItems((prev) => {
      if (quantity <= 0) {
        const copy = { ...prev };
        delete copy[productId];
        return copy;
      }
      return { ...prev, [productId]: { ...prev[productId], quantity } };
    });
  };

  const removeFromCart = (productId) => {
    setItems((prev) => {
      const copy = { ...prev };
      delete copy[productId];
      return copy;
    });
  };

  const clearCart = () => setItems({});

  const cartList = useMemo(() => Object.values(items), [items]);
  const totalItemCount = useMemo(
    () => cartList.reduce((sum, i) => sum + i.quantity, 0),
    [cartList]
  );

  return (
    <CartContext.Provider
      value={{
        items,
        cartList,
        totalItemCount,
        addToCart,
        updateQuantity,
        removeFromCart,
        clearCart,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart, CartProvider içinde kullanılmalı');
  return ctx;
}
