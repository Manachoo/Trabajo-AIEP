import { useCallback, useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { ShoppingCart, UtensilsCrossed, AlertCircle, CheckCircle } from 'lucide-react'

import { Button } from './components/ui/button'

interface ApiProduct {
  id: number
  restaurant_id: number
  name: string
  price: number
  stock: number
}

interface Product {
  id: number
  restaurantId: number
  name: string
  price: number
  stock: number
}

interface OrderResponse {
  message: string
  order_id: number
  total: number
  new_user_balance: number
}

interface Notification {
  type: 'error' | 'success'
  text: string
}

const API_URL = 'http://localhost:8000'
const CURRENT_USER_ID = 1
const CURRENT_USER_NAME = 'John Perez'

const mapApiProductToProduct = (product: ApiProduct): Product => ({
  id: product.id,
  restaurantId: product.restaurant_id,
  name: product.name,
  price: product.price,
  stock: product.stock,
})

function App() {
  const { t, i18n } = useTranslation('common')
  const [products, setProducts] = useState<Product[]>([])
  const [cart, setCart] = useState<Product[]>([])
  const [loading, setLoading] = useState(false)
  const [notification, setNotification] = useState<Notification | null>(null)

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat(i18n.resolvedLanguage ?? 'en', {
      style: 'currency',
      currency: 'USD',
    }).format(value)

  const fetchProducts = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/products`)
      if (!response.ok) {
        throw new Error(t('errors.fetchProducts'))
      }
      const data: ApiProduct[] = await response.json()
      setProducts(data.map(mapApiProductToProduct))
    } catch (error) {
      console.error(error)
      setNotification({ type: 'error', text: t('errors.fetchProducts') })
    }
  }, [t])

  useEffect(() => {
    void fetchProducts()
  }, [fetchProducts])

  const addToCart = (product: Product) => {
    setCart([...cart, product])
  }

  const removeFromCart = (index: number) => {
    const nextCart = [...cart]
    nextCart.splice(index, 1)
    setCart(nextCart)
  }

  const submitOrder = async () => {
    if (cart.length === 0) {
      return
    }

    setLoading(true)
    setNotification(null)

    try {
      const productIds = cart.map((product) => product.id)
      const response = await fetch(`${API_URL}/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: CURRENT_USER_ID,
          product_ids: productIds,
        }),
      })

      const payload = await response.json()

      if (!response.ok) {
        const detail = typeof payload?.detail === 'string' ? payload.detail : t('errors.processOrder')
        throw new Error(detail)
      }

      const data = payload as OrderResponse
      setNotification({
        type: 'success',
        text: t('messages.orderPaid', {
          balance: formatCurrency(data.new_user_balance),
        }),
      })
      setCart([])
      await fetchProducts()
    } catch (error) {
      const message = error instanceof Error ? error.message : t('errors.processOrder')
      setNotification({ type: 'error', text: message })
    } finally {
      setLoading(false)
    }
  }

  const total = cart.reduce((accumulator, item) => accumulator + item.price, 0)

  return (
    <div className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <header className="flex items-center justify-between border-b border-border pb-6">
          <div className="flex items-center gap-3">
            <div className="bg-primary p-2 rounded-lg text-primary-foreground">
              <UtensilsCrossed size={28} />
            </div>
            <h1 className="text-3xl font-bold tracking-tight">{t('app.title')}</h1>
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            {t('header.greeting')},{' '}
            <span className="text-foreground font-medium">
              {t('header.userLabel', { name: CURRENT_USER_NAME, id: CURRENT_USER_ID })}
            </span>
          </div>
        </header>

        {notification && (
          <div
            className={`p-4 rounded-md border flex items-center gap-3 ${
              notification.type === 'success'
                ? 'bg-green-500/10 border-green-500/50 text-green-600'
                : 'bg-red-500/10 border-destructive/50 text-destructive'
            }`}
          >
            {notification.type === 'success' ? <CheckCircle /> : <AlertCircle />}
            <span className="font-medium">{notification.text}</span>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-6">
            <h2 className="text-xl font-semibold">{t('products.title')}</h2>
            <div className="rounded-md border border-border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted">
                  <tr>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                      {t('products.table.name')}
                    </th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                      {t('products.table.price')}
                    </th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                      {t('products.table.stock')}
                    </th>
                    <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">
                      {t('products.table.action')}
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {products.map((product) => (
                    <tr key={product.id} className="hover:bg-muted/50 transition-colors">
                      <td className="p-4 align-middle font-medium">{product.name}</td>
                      <td className="p-4 align-middle">{formatCurrency(product.price)}</td>
                      <td className="p-4 align-middle">
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-semibold ${
                            product.stock > 5
                              ? 'bg-green-500/20 text-green-500'
                              : 'bg-yellow-500/20 text-yellow-500'
                          }`}
                        >
                          {t('products.table.units', { count: product.stock })}
                        </span>
                      </td>
                      <td className="p-4 align-middle text-right">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => addToCart(product)}
                          disabled={loading || product.stock <= 0}
                        >
                          {t('products.add')}
                        </Button>
                      </td>
                    </tr>
                  ))}
                  {products.length === 0 && (
                    <tr>
                      <td colSpan={4} className="p-4 text-center text-muted-foreground">
                        {t('products.emptyState')}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="md:col-span-1">
            <div className="border border-border rounded-xl p-6 bg-card flex flex-col h-full shadow-sm">
              <div className="flex items-center gap-2 mb-6">
                <ShoppingCart className="text-primary" />
                <h2 className="text-xl font-semibold">{t('cart.title')}</h2>
              </div>

              <div className="flex-1 overflow-y-auto space-y-4 mb-6">
                {cart.length === 0 ? (
                  <p className="text-muted-foreground text-sm">{t('cart.empty')}</p>
                ) : (
                  cart.map((item, index) => (
                    <div key={index} className="flex justify-between items-center text-sm">
                      <span className="truncate pr-4">{item.name}</span>
                      <div className="flex items-center gap-3">
                        <span className="font-semibold">{formatCurrency(item.price)}</span>
                        <button
                          onClick={() => removeFromCart(index)}
                          className="text-destructive hover:underline text-xs"
                          disabled={loading}
                        >
                          {t('cart.remove')}
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>

              <div className="border-t border-border pt-4 mt-auto">
                <div className="flex justify-between items-center mb-6">
                  <span className="font-medium text-lg">{t('cart.total')}</span>
                  <span className="text-2xl font-bold tracking-tight">{formatCurrency(total)}</span>
                </div>
                <Button
                  className="w-full text-lg h-12"
                  onClick={submitOrder}
                  disabled={cart.length === 0 || loading}
                >
                  {loading ? t('cart.processing') : t('cart.checkout')}
                </Button>
                <p className="text-xs text-muted-foreground mt-4 text-center">{t('cart.footerNote')}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
