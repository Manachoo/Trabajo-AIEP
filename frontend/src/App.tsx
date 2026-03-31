import { useState, useEffect } from 'react'
import { ShoppingCart, UtensilsCrossed, AlertCircle, CheckCircle } from 'lucide-react'
import { Button } from './components/ui/button'

interface Producto {
  id: number
  restaurante_id: number
  nombre: string
  precio: number
  stock: number
}

function App() {
  const [productos, setProductos] = useState<Producto[]>([])
  const [carrito, setCarrito] = useState<Producto[]>([])
  const [loading, setLoading] = useState(false)
  const [mensaje, setMensaje] = useState<{ tipo: 'error' | 'success', texto: string } | null>(null)

  const API_URL = "http://localhost:8000"
  
  // Usuario Dummy (simulando autenticación)
  const usuario_id = 1

  useEffect(() => {
    fetchProductos()
  }, [])

  const fetchProductos = async () => {
    try {
      const res = await fetch(`${API_URL}/productos`)
      const data = await res.json()
      setProductos(data)
    } catch (e) {
      console.error(e)
    }
  }

  const agregarAlCarrito = (producto: Producto) => {
    setCarrito([...carrito, producto])
  }

  const removerDelCarrito = (index: number) => {
    const nuevoCarrito = [...carrito]
    nuevoCarrito.splice(index, 1)
    setCarrito(nuevoCarrito)
  }

  const procesarPedido = async () => {
    if (carrito.length === 0) return
    
    setLoading(true)
    setMensaje(null)
    try {
      const productoIds = carrito.map(p => p.id)
      const res = await fetch(`${API_URL}/pedido`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          usuario_id,
          productos_ids: productoIds
        })
      })
      
      const data = await res.json()
      
      if (!res.ok) {
        throw new Error(data.detail || "Error al procesar el pedido")
      }
      
      setMensaje({ tipo: 'success', texto: `¡Pedido pagado! Nuevo saldo: $${data.nuevo_saldo_usuario}` })
      setCarrito([])
      fetchProductos() // Actualizar stock
      
    } catch (error: any) {
      setMensaje({ tipo: 'error', texto: error.message })
    } finally {
      setLoading(false)
    }
  }

  const total = carrito.reduce((acc, obj) => acc + obj.precio, 0)

  return (
    <div className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <header className="flex items-center justify-between border-b border-border pb-6">
          <div className="flex items-center gap-3">
            <div className="bg-primary p-2 rounded-lg text-primary-foreground">
              <UtensilsCrossed size={28} />
            </div>
            <h1 className="text-3xl font-bold tracking-tight">Food Delivery</h1>
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            Hola, <span className="text-foreground font-medium">Juan Perez (ID: {usuario_id})</span>
          </div>
        </header>

        {mensaje && (
          <div className={`p-4 rounded-md border flex items-center gap-3 ${
            mensaje.tipo === 'success' 
            ? 'bg-green-500/10 border-green-500/50 text-green-600' 
            : 'bg-red-500/10 border-destructive/50 text-destructive'
          }`}>
            {mensaje.tipo === 'success' ? <CheckCircle /> : <AlertCircle />}
            <span className="font-medium">{mensaje.texto}</span>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          <div className="md:col-span-2 space-y-6">
            <h2 className="text-xl font-semibold">Productos Disponibles</h2>
            <div className="rounded-md border border-border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted">
                  <tr>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Nombre</th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Precio</th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Stock</th>
                    <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">Acción</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {productos.map((producto) => (
                    <tr key={producto.id} className="hover:bg-muted/50 transition-colors">
                      <td className="p-4 align-middle font-medium">{producto.nombre}</td>
                      <td className="p-4 align-middle">${producto.precio.toFixed(2)}</td>
                      <td className="p-4 align-middle">
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${producto.stock > 5 ? 'bg-green-500/20 text-green-500' : 'bg-yellow-500/20 text-yellow-500'}`}>
                          {producto.stock} uds
                        </span>
                      </td>
                      <td className="p-4 align-middle text-right">
                        <Button 
                          variant="secondary" 
                          size="sm"
                          onClick={() => agregarAlCarrito(producto)}
                          disabled={loading || producto.stock <= 0}
                        >
                          Añadir
                        </Button>
                      </td>
                    </tr>
                  ))}
                  {productos.length === 0 && (
                    <tr>
                      <td colSpan={4} className="p-4 text-center text-muted-foreground">
                        Cargando productos o sin stock...
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
                <h2 className="text-xl font-semibold">Tu Pedido</h2>
              </div>
              
              <div className="flex-1 overflow-y-auto space-y-4 mb-6">
                {carrito.length === 0 ? (
                  <p className="text-muted-foreground text-sm">El carrito está vacío.</p>
                ) : (
                  carrito.map((item, index) => (
                    <div key={index} className="flex justify-between items-center text-sm">
                      <span className="truncate pr-4">{item.nombre}</span>
                      <div className="flex items-center gap-3">
                        <span className="font-semibold">${item.precio.toFixed(2)}</span>
                        <button 
                          onClick={() => removerDelCarrito(index)}
                          className="text-destructive hover:underline text-xs"
                          disabled={loading}
                        >
                          Quitar
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>

              <div className="border-t border-border pt-4 mt-auto">
                <div className="flex justify-between items-center mb-6">
                  <span className="font-medium text-lg">Total</span>
                  <span className="text-2xl font-bold tracking-tight">${total.toFixed(2)}</span>
                </div>
                <Button 
                  className="w-full text-lg h-12"
                  onClick={procesarPedido}
                  disabled={carrito.length === 0 || loading}
                >
                  {loading ? "Procesando el pago..." : "Pagar y Finalizar"}
                </Button>
                <p className="text-xs text-muted-foreground mt-4 text-center">
                  Al pagar se invocará la God Class del backend que procesa stock y pago en una sola transacción defectuosa.
                </p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}

export default App
