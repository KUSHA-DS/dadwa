"use client";

import { useState } from "react";
import useSWR, { mutate } from "swr";
import {
  Package,
  Plus,
  Minus,
  Trash2,
  Search,
  Box,
  TrendingUp,
  AlertTriangle,
  Edit2,
  X,
  Check,
  ImageIcon,
} from "lucide-react";
import Image from "next/image";

interface Product {
  id: number;
  name: string;
  category: string;
  size: string | null;
  color: string | null;
  price: number;
  stock: number;
  min_stock: number;
  image_url: string | null;
  created_at: string;
  updated_at: string;
}

interface Stats {
  total_products: number;
  total_stock: number;
  low_stock_count: number;
  total_value: number;
}

const fetcher = (url: string) => fetch(url).then((res) => res.json());

const categories = [
  { value: "doreza", label: "Doreza Boksi" },
  { value: "tesha", label: "Tesha Boksi" },
  { value: "atlete", label: "Atlete" },
  { value: "pantallona", label: "Pantallona" },
  { value: "koka", label: "Mbrojtese Koke" },
  { value: "dhembe", label: "Mbrojtese Dhembesh" },
  { value: "trastë", label: "Traste Boksi" },
  { value: "thes", label: "Thes Boksi" },
  { value: "tjeter", label: "Tjeter" },
];

export default function Home() {
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  const { data: products, isLoading: productsLoading } = useSWR<Product[]>(
    `/api/products?search=${searchTerm}&category=${categoryFilter}`,
    fetcher
  );

  const { data: stats } = useSWR<Stats>("/api/stats", fetcher);

  const updateStock = async (id: number, change: number) => {
    await fetch(`/api/products/${id}/stock`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ change }),
    });
    mutate(`/api/products?search=${searchTerm}&category=${categoryFilter}`);
    mutate("/api/stats");
  };

  const deleteProduct = async (id: number) => {
    if (!confirm("A je i sigurt qe deshiron ta fshish kete produkt?")) return;
    await fetch(`/api/products/${id}`, { method: "DELETE" });
    mutate(`/api/products?search=${searchTerm}&category=${categoryFilter}`);
    mutate("/api/stats");
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary rounded-lg">
              <Package className="w-8 h-8 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                Boxing Store
              </h1>
              <p className="text-muted-foreground text-sm">
                Menaxhimi i Stokut
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <StatCard
            icon={<Box className="w-5 h-5" />}
            label="Produkte Totale"
            value={stats?.total_products ?? 0}
          />
          <StatCard
            icon={<Package className="w-5 h-5" />}
            label="Stok Total"
            value={stats?.total_stock ?? 0}
          />
          <StatCard
            icon={<AlertTriangle className="w-5 h-5" />}
            label="Stok i Ulet"
            value={stats?.low_stock_count ?? 0}
            warning
          />
          <StatCard
            icon={<TrendingUp className="w-5 h-5" />}
            label="Vlera Totale"
            value={`€${(stats?.total_value ?? 0).toFixed(2)}`}
          />
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Kerko produkte..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-card border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-4 py-2.5 bg-card border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">Te gjitha kategorite</option>
            {categories.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium"
          >
            <Plus className="w-5 h-5" />
            Shto Produkt
          </button>
        </div>

        {/* Products Table */}
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-secondary">
                <tr>
                  <th className="text-left px-4 py-3 text-sm font-semibold text-foreground">
                    Foto
                  </th>
                  <th className="text-left px-4 py-3 text-sm font-semibold text-foreground">
                    Produkti
                  </th>
                  <th className="text-left px-4 py-3 text-sm font-semibold text-foreground">
                    Kategoria
                  </th>
                  <th className="text-left px-4 py-3 text-sm font-semibold text-foreground">
                    Madhesia
                  </th>
                  <th className="text-left px-4 py-3 text-sm font-semibold text-foreground">
                    Cmimi
                  </th>
                  <th className="text-left px-4 py-3 text-sm font-semibold text-foreground">
                    Stoku
                  </th>
                  <th className="text-left px-4 py-3 text-sm font-semibold text-foreground">
                    Veprimet
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {productsLoading ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center">
                      <div className="flex items-center justify-center gap-2 text-muted-foreground">
                        <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                        Duke ngarkuar...
                      </div>
                    </td>
                  </tr>
                ) : products?.length === 0 ? (
                  <tr>
                    <td
                      colSpan={7}
                      className="px-4 py-8 text-center text-muted-foreground"
                    >
                      Nuk u gjeten produkte
                    </td>
                  </tr>
                ) : (
                  products?.map((product) => (
                    <tr
                      key={product.id}
                      className="hover:bg-secondary/50 transition-colors"
                    >
                      <td className="px-4 py-3">
                        {product.image_url ? (
                          <div className="w-12 h-12 relative rounded-lg overflow-hidden bg-secondary">
                            <Image
                              src={product.image_url}
                              alt={product.name}
                              fill
                              className="object-cover"
                              unoptimized
                            />
                          </div>
                        ) : (
                          <div className="w-12 h-12 rounded-lg bg-secondary flex items-center justify-center">
                            <ImageIcon className="w-5 h-5 text-muted-foreground" />
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <div>
                          <p className="font-medium text-foreground">
                            {product.name}
                          </p>
                          {product.color && (
                            <p className="text-sm text-muted-foreground">
                              {product.color}
                            </p>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 bg-secondary text-secondary-foreground text-sm rounded">
                          {categories.find((c) => c.value === product.category)
                            ?.label || product.category}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {product.size || "-"}
                      </td>
                      <td className="px-4 py-3 font-medium text-foreground">
                        €{product.price.toFixed(2)}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`px-2 py-1 rounded text-sm font-medium ${
                            product.stock <= product.min_stock
                              ? "bg-destructive/20 text-destructive"
                              : product.stock <= product.min_stock * 2
                                ? "bg-warning/20 text-warning"
                                : "bg-success/20 text-success"
                          }`}
                        >
                          {product.stock}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => updateStock(product.id, -1)}
                            disabled={product.stock <= 0}
                            className="p-1.5 rounded hover:bg-secondary disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                            title="Hiq nga stoku"
                          >
                            <Minus className="w-4 h-4 text-muted-foreground" />
                          </button>
                          <button
                            onClick={() => updateStock(product.id, 1)}
                            className="p-1.5 rounded hover:bg-secondary transition-colors"
                            title="Shto ne stok"
                          >
                            <Plus className="w-4 h-4 text-muted-foreground" />
                          </button>
                          <button
                            onClick={() => setEditingProduct(product)}
                            className="p-1.5 rounded hover:bg-secondary transition-colors"
                            title="Ndrysho"
                          >
                            <Edit2 className="w-4 h-4 text-muted-foreground" />
                          </button>
                          <button
                            onClick={() => deleteProduct(product.id)}
                            className="p-1.5 rounded hover:bg-destructive/20 transition-colors"
                            title="Fshij"
                          >
                            <Trash2 className="w-4 h-4 text-destructive" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Add Product Modal */}
      {showAddModal && (
        <ProductModal
          onClose={() => setShowAddModal(false)}
          onSuccess={() => {
            setShowAddModal(false);
            mutate(
              `/api/products?search=${searchTerm}&category=${categoryFilter}`
            );
            mutate("/api/stats");
          }}
        />
      )}

      {/* Edit Product Modal */}
      {editingProduct && (
        <ProductModal
          product={editingProduct}
          onClose={() => setEditingProduct(null)}
          onSuccess={() => {
            setEditingProduct(null);
            mutate(
              `/api/products?search=${searchTerm}&category=${categoryFilter}`
            );
            mutate("/api/stats");
          }}
        />
      )}
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  warning,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  warning?: boolean;
}) {
  return (
    <div className="bg-card border border-border rounded-lg p-4">
      <div className="flex items-center gap-3">
        <div
          className={`p-2 rounded-lg ${warning ? "bg-warning/20 text-warning" : "bg-primary/20 text-primary"}`}
        >
          {icon}
        </div>
        <div>
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="text-xl font-bold text-foreground">{value}</p>
        </div>
      </div>
    </div>
  );
}

function ProductModal({
  product,
  onClose,
  onSuccess,
}: {
  product?: Product;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [formData, setFormData] = useState({
    name: product?.name || "",
    category: product?.category || "doreza",
    size: product?.size || "",
    color: product?.color || "",
    price: product?.price?.toString() || "",
    stock: product?.stock?.toString() || "",
    min_stock: product?.min_stock?.toString() || "5",
    image_url: product?.image_url || "",
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    const payload = {
      name: formData.name,
      category: formData.category,
      size: formData.size || null,
      color: formData.color || null,
      price: parseFloat(formData.price),
      stock: parseInt(formData.stock),
      min_stock: parseInt(formData.min_stock),
      image_url: formData.image_url || null,
    };

    if (product) {
      await fetch(`/api/products/${product.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } else {
      await fetch("/api/products", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    }

    setLoading(false);
    onSuccess();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-card border border-border rounded-lg w-full max-w-md">
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          <h2 className="text-lg font-semibold text-foreground">
            {product ? "Ndrysho Produktin" : "Shto Produkt te Ri"}
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-secondary transition-colors"
          >
            <X className="w-5 h-5 text-muted-foreground" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Emri i Produktit
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="p.sh. Doreza Everlast Pro"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Kategoria
            </label>
            <select
              value={formData.category}
              onChange={(e) =>
                setFormData({ ...formData, category: e.target.value })
              }
              className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {categories.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Madhesia
              </label>
              <input
                type="text"
                value={formData.size}
                onChange={(e) =>
                  setFormData({ ...formData, size: e.target.value })
                }
                className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="p.sh. M, L, 12oz"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Ngjyra
              </label>
              <input
                type="text"
                value={formData.color}
                onChange={(e) =>
                  setFormData({ ...formData, color: e.target.value })
                }
                className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="p.sh. Zi, Kuqe"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              URL e Fotos
            </label>
            <div className="flex gap-2">
              <input
                type="url"
                value={formData.image_url}
                onChange={(e) =>
                  setFormData({ ...formData, image_url: e.target.value })
                }
                className="flex-1 px-3 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="https://example.com/foto.jpg"
              />
              {formData.image_url && (
                <div className="w-10 h-10 relative rounded-lg overflow-hidden bg-secondary flex-shrink-0">
                  <Image
                    src={formData.image_url}
                    alt="Preview"
                    fill
                    className="object-cover"
                    unoptimized
                  />
                </div>
              )}
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Cmimi (€)
              </label>
              <input
                type="number"
                required
                step="0.01"
                min="0"
                value={formData.price}
                onChange={(e) =>
                  setFormData({ ...formData, price: e.target.value })
                }
                className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Stoku
              </label>
              <input
                type="number"
                required
                min="0"
                value={formData.stock}
                onChange={(e) =>
                  setFormData({ ...formData, stock: e.target.value })
                }
                className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Min Stok
              </label>
              <input
                type="number"
                required
                min="0"
                value={formData.min_stock}
                onChange={(e) =>
                  setFormData({ ...formData, min_stock: e.target.value })
                }
                className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2.5 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-colors font-medium"
            >
              Anulo
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors font-medium"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <Check className="w-4 h-4" />
                  {product ? "Ruaj" : "Shto"}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
