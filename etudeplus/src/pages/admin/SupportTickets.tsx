import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/contexts/AuthContext";
import { useTenant } from "@/contexts/TenantContext";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";
import {
  TicketStatus,
  TicketPriority,
  TicketCategory,
  priorityColors,
  statusColors,
  categoryLabels,
} from "@/lib/support-types";
import {
  Headphones,
  Plus,
  Search,
  Filter,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  MessageSquare,
  Wrench,
  Monitor,
  Server,
  Wifi,
  Users,
  GraduationCap,
  FileText,
  MoreHorizontal,
} from "lucide-react";

const categoryIcons: Record<TicketCategory, React.ReactNode> = {
  technical: <Monitor className="h-4 w-4" />,
  maintenance: <Wrench className="h-4 w-4" />,
  software: <Server className="h-4 w-4" />,
  hardware: <Monitor className="h-4 w-4" />,
  network: <Wifi className="h-4 w-4" />,
  user_support: <Users className="h-4 w-4" />,
  academic: <GraduationCap className="h-4 w-4" />,
  administrative: <FileText className="h-4 w-4" />,
  other: <MoreHorizontal className="h-4 w-4" />,
};

export default function SupportTickets() {
  const { user } = useAuth();
  const { tenant } = useTenant();
  const queryClient = useQueryClient();
  const [isOpen, setIsOpen] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [priorityFilter, setPriorityFilter] = useState<string>("all");

  // Form state
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    category: "other" as TicketCategory,
    priority: "medium" as TicketPriority,
    location: "",
    asset_id: "",
    asset_name: "",
  });

  // Query tickets
  const { data: tickets = [], isLoading } = useQuery({
    queryKey: ["support-tickets", tenant?.id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("support_tickets")
        .select(`
          *,
          reporter:users!support_tickets_reported_by_fkey(first_name, last_name),
          assignee:users!support_tickets_assigned_to_fkey(first_name, last_name)
        `)
        .eq("tenant_id", tenant?.id)
        .order("created_at", { ascending: false });

      if (error) throw error;
      return data || [];
    },
    enabled: !!tenant?.id,
  });

  // Create ticket mutation
  const createMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const ticketNumber = `TKT-${Date.now().toString(36).toUpperCase()}`;

      const { error } = await supabase.from("support_tickets").insert({
        tenant_id: tenant?.id,
        ticket_number: ticketNumber,
        title: data.title,
        description: data.description,
        category: data.category,
        priority: data.priority,
        location: data.location || null,
        asset_id: data.asset_id || null,
        asset_name: data.asset_name || null,
        reported_by: user?.id,
      });

      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["support-tickets"] });
      setIsOpen(false);
      resetForm();
      toast.success("Ticket créé avec succès");
    },
    onError: (error: any) => {
      toast.error(`Erreur: ${error.message}`);
    },
  });

  // Update status mutation
  const updateStatusMutation = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: TicketStatus }) => {
      const updates: any = { status };
      if (status === "resolved") {
        updates.resolved_at = new Date().toISOString();
      } else if (status === "closed") {
        updates.closed_at = new Date().toISOString();
      }

      const { error } = await supabase
        .from("support_tickets")
        .update(updates)
        .eq("id", id);

      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["support-tickets"] });
      toast.success("Statut mis à jour");
    },
  });

  const resetForm = () => {
    setFormData({
      title: "",
      description: "",
      category: "other",
      priority: "medium",
      location: "",
      asset_id: "",
      asset_name: "",
    });
  };

  const filteredTickets = tickets.filter((ticket: any) => {
    const matchesSearch =
      ticket.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.ticket_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.description?.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus = statusFilter === "all" || ticket.status === statusFilter;
    const matchesPriority = priorityFilter === "all" || ticket.priority === priorityFilter;

    return matchesSearch && matchesStatus && matchesPriority;
  });

  const openTickets = filteredTickets.filter((t: any) =>
    ["open", "in_progress", "pending", "reopened"].includes(t.status)
  );
  const closedTickets = filteredTickets.filter((t: any) =>
    ["resolved", "closed"].includes(t.status)
  );

  const stats = {
    total: tickets.length,
    open: tickets.filter((t: any) => t.status === "open" || t.status === "reopened").length,
    inProgress: tickets.filter((t: any) => t.status === "in_progress" || t.status === "pending").length,
    resolved: tickets.filter((t: any) => t.status === "resolved").length,
    critical: tickets.filter(
      (t: any) =>
        (t.priority === "critical" || t.priority === "urgent") &&
        !["resolved", "closed"].includes(t.status)
    ).length,
    overdue: tickets.filter(
      (t: any) => t.sla_due_date && new Date(t.sla_due_date) < new Date()
    ).length,
  };

  const getPriorityBadge = (priority: TicketPriority) => {
    const colors: Record<TicketPriority, string> = {
      low: "bg-gray-100 text-gray-800",
      medium: "bg-blue-100 text-blue-800",
      high: "bg-orange-100 text-orange-800",
      critical: "bg-red-100 text-red-800",
      urgent: "bg-purple-100 text-purple-800",
    };
    const labels: Record<TicketPriority, string> = {
      low: "Basse",
      medium: "Moyenne",
      high: "Haute",
      critical: "Critique",
      urgent: "Urgent",
    };
    return <Badge className={colors[priority]}>{labels[priority]}</Badge>;
  };

  const getStatusBadge = (status: TicketStatus) => {
    const colors: Record<TicketStatus, string> = {
      open: "bg-blue-100 text-blue-800",
      in_progress: "bg-yellow-100 text-yellow-800",
      pending: "bg-orange-100 text-orange-800",
      resolved: "bg-green-100 text-green-800",
      closed: "bg-gray-100 text-gray-800",
      reopened: "bg-purple-100 text-purple-800",
    };
    const labels: Record<TicketStatus, string> = {
      open: "Ouvert",
      in_progress: "En cours",
      pending: "En attente",
      resolved: "Résolu",
      closed: "Fermé",
      reopened: "Réouvert",
    };
    return <Badge className={colors[status]}>{labels[status]}</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Headphones className="h-6 w-6" />
            Support & Maintenance
          </h1>
          <p className="text-muted-foreground">
            Gérez les tickets de support et demandes de maintenance
          </p>
        </div>
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => setIsOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Nouveau Ticket
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Créer un ticket de support</DialogTitle>
            </DialogHeader>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                createMutation.mutate(formData);
              }}
              className="space-y-4"
            >
              <div>
                <label className="text-sm font-medium">Titre *</label>
                <Input
                  value={formData.title}
                  onChange={(e) =>
                    setFormData({ ...formData, title: e.target.value })
                  }
                  placeholder="Description courte du problème"
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium">Description</label>
                <Textarea
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  placeholder="Décrivez le problème en détail..."
                  rows={4}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Catégorie</label>
                  <Select
                    value={formData.category}
                    onValueChange={(value: TicketCategory) =>
                      setFormData({ ...formData, category: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="technical">Technique</SelectItem>
                      <SelectItem value="maintenance">Maintenance</SelectItem>
                      <SelectItem value="software">Logiciel</SelectItem>
                      <SelectItem value="hardware">Matériel</SelectItem>
                      <SelectItem value="network">Réseau</SelectItem>
                      <SelectItem value="user_support">Support Utilisateur</SelectItem>
                      <SelectItem value="academic">Académique</SelectItem>
                      <SelectItem value="administrative">Administratif</SelectItem>
                      <SelectItem value="other">Autre</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium">Priorité</label>
                  <Select
                    value={formData.priority}
                    onValueChange={(value: TicketPriority) =>
                      setFormData({ ...formData, priority: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Basse</SelectItem>
                      <SelectItem value="medium">Moyenne</SelectItem>
                      <SelectItem value="high">Haute</SelectItem>
                      <SelectItem value="critical">Critique</SelectItem>
                      <SelectItem value="urgent">Urgent</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Lieu</label>
                  <Input
                    value={formData.location}
                    onChange={(e) =>
                      setFormData({ ...formData, location: e.target.value })
                    }
                    placeholder="Salle, bâtiment, etc."
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Équipement</label>
                  <Input
                    value={formData.asset_name}
                    onChange={(e) =>
                      setFormData({ ...formData, asset_name: e.target.value })
                    }
                    placeholder="Nom de l'équipement"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsOpen(false)}
                >
                  Annuler
                </Button>
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? "Création..." : "Créer le ticket"}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-sm text-muted-foreground">Total</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-blue-600">{stats.open}</div>
            <p className="text-sm text-muted-foreground">Ouverts</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-yellow-600">
              {stats.inProgress}
            </div>
            <p className="text-sm text-muted-foreground">En cours</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-green-600">
              {stats.resolved}
            </div>
            <p className="text-sm text-muted-foreground">Résolus</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-red-600">{stats.critical}</div>
            <p className="text-sm text-muted-foreground">Critiques</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-purple-600">
              {stats.overdue}
            </div>
            <p className="text-sm text-muted-foreground">En retard SLA</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Rechercher par titre, numéro ou description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Statut" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous les statuts</SelectItem>
            <SelectItem value="open">Ouvert</SelectItem>
            <SelectItem value="in_progress">En cours</SelectItem>
            <SelectItem value="pending">En attente</SelectItem>
            <SelectItem value="resolved">Résolu</SelectItem>
            <SelectItem value="closed">Fermé</SelectItem>
          </SelectContent>
        </Select>
        <Select value={priorityFilter} onValueChange={setPriorityFilter}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Priorité" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Toutes les priorités</SelectItem>
            <SelectItem value="low">Basse</SelectItem>
            <SelectItem value="medium">Moyenne</SelectItem>
            <SelectItem value="high">Haute</SelectItem>
            <SelectItem value="critical">Critique</SelectItem>
            <SelectItem value="urgent">Urgent</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Tickets Tabs */}
      <Tabs defaultValue="open" className="space-y-4">
        <TabsList>
          <TabsTrigger value="open">
            En cours ({openTickets.length})
          </TabsTrigger>
          <TabsTrigger value="closed">
            Clôturés ({closedTickets.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="open">
          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>N° Ticket</TableHead>
                  <TableHead>Titre</TableHead>
                  <TableHead>Catégorie</TableHead>
                  <TableHead>Priorité</TableHead>
                  <TableHead>Statut</TableHead>
                  <TableHead>Assigné à</TableHead>
                  <TableHead>Créé le</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center">
                      Chargement...
                    </TableCell>
                  </TableRow>
                ) : openTickets.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center">
                      Aucun ticket en cours
                    </TableCell>
                  </TableRow>
                ) : (
                  openTickets.map((ticket: any) => (
                    <TableRow key={ticket.id}>
                      <TableCell className="font-mono text-sm">
                        {ticket.ticket_number}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {categoryIcons[ticket.category as TicketCategory]}
                          <span>{ticket.title}</span>
                        </div>
                      </TableCell>
                      <TableCell className="capitalize">
                        {ticket.category.replace("_", " ")}
                      </TableCell>
                      <TableCell>{getPriorityBadge(ticket.priority)}</TableCell>
                      <TableCell>{getStatusBadge(ticket.status)}</TableCell>
                      <TableCell>
                        {ticket.assignee
                          ? `${ticket.assignee.first_name} ${ticket.assignee.last_name}`
                          : "Non assigné"}
                      </TableCell>
                      <TableCell>
                        {new Date(ticket.created_at).toLocaleDateString("fr-FR")}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          {ticket.status === "open" && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() =>
                                updateStatusMutation.mutate({
                                  id: ticket.id,
                                  status: "in_progress",
                                })
                              }
                            >
                              Prendre en charge
                            </Button>
                          )}
                          {ticket.status === "in_progress" && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() =>
                                updateStatusMutation.mutate({
                                  id: ticket.id,
                                  status: "resolved",
                                })
                              }
                            >
                              Résoudre
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        <TabsContent value="closed">
          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>N° Ticket</TableHead>
                  <TableHead>Titre</TableHead>
                  <TableHead>Catégorie</TableHead>
                  <TableHead>Priorité</TableHead>
                  <TableHead>Statut</TableHead>
                  <TableHead>Résolu le</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {closedTickets.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center">
                      Aucun ticket clôturé
                    </TableCell>
                  </TableRow>
                ) : (
                  closedTickets.map((ticket: any) => (
                    <TableRow key={ticket.id}>
                      <TableCell className="font-mono text-sm">
                        {ticket.ticket_number}
                      </TableCell>
                      <TableCell>{ticket.title}</TableCell>
                      <TableCell className="capitalize">
                        {ticket.category.replace("_", " ")}
                      </TableCell>
                      <TableCell>{getPriorityBadge(ticket.priority)}</TableCell>
                      <TableCell>{getStatusBadge(ticket.status)}</TableCell>
                      <TableCell>
                        {ticket.resolved_at
                          ? new Date(ticket.resolved_at).toLocaleDateString("fr-FR")
                          : "-"}
                      </TableCell>
                      <TableCell>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() =>
                            updateStatusMutation.mutate({
                              id: ticket.id,
                              status: "reopened",
                            })
                          }
                        >
                          Réouvrir
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
