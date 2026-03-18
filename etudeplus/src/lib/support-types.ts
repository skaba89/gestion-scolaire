/**
 * Support Ticket Types for GropAgent - Support and Maintenance Management
 */

export type TicketStatus =
  | "open"
  | "in_progress"
  | "pending"
  | "resolved"
  | "closed"
  | "reopened";

export type TicketPriority =
  | "low"
  | "medium"
  | "high"
  | "critical"
  | "urgent";

export type TicketCategory =
  | "technical"
  | "maintenance"
  | "software"
  | "hardware"
  | "network"
  | "user_support"
  | "academic"
  | "administrative"
  | "other";

export const statusColors: Record<TicketStatus, string> = {
  open: "bg-blue-100 text-blue-800 border-blue-200",
  in_progress: "bg-yellow-100 text-yellow-800 border-yellow-200",
  pending: "bg-orange-100 text-orange-800 border-orange-200",
  resolved: "bg-green-100 text-green-800 border-green-200",
  closed: "bg-gray-100 text-gray-800 border-gray-200",
  reopened: "bg-purple-100 text-purple-800 border-purple-200",
};

export const priorityColors: Record<TicketPriority, string> = {
  low: "bg-gray-100 text-gray-800 border-gray-200",
  medium: "bg-blue-100 text-blue-800 border-blue-200",
  high: "bg-orange-100 text-orange-800 border-orange-200",
  critical: "bg-red-100 text-red-800 border-red-200",
  urgent: "bg-purple-100 text-purple-800 border-purple-200",
};

export const statusLabels: Record<TicketStatus, string> = {
  open: "Ouvert",
  in_progress: "En cours",
  pending: "En attente",
  resolved: "Résolu",
  closed: "Fermé",
  reopened: "Réouvert",
};

export const priorityLabels: Record<TicketPriority, string> = {
  low: "Basse",
  medium: "Moyenne",
  high: "Haute",
  critical: "Critique",
  urgent: "Urgent",
};

export const categoryLabels: Record<TicketCategory, string> = {
  technical: "Technique",
  maintenance: "Maintenance",
  software: "Logiciel",
  hardware: "Matériel",
  network: "Réseau",
  user_support: "Support Utilisateur",
  academic: "Académique",
  administrative: "Administratif",
  other: "Autre",
};

export const categoryIcons: Record<TicketCategory, string> = {
  technical: "monitor",
  maintenance: "wrench",
  software: "server",
  hardware: "hard-drive",
  network: "wifi",
  user_support: "users",
  academic: "graduation-cap",
  administrative: "file-text",
  other: "more-horizontal",
};

export interface SupportTicket {
  id: string;
  tenant_id: string;
  ticket_number: string;
  title: string;
  description?: string;
  category: TicketCategory;
  priority: TicketPriority;
  status: TicketStatus;
  reported_by?: string;
  reporter?: {
    first_name?: string;
    last_name?: string;
  };
  assigned_to?: string;
  assignee?: {
    first_name?: string;
    last_name?: string;
  };
  assigned_department?: string;
  location?: string;
  asset_id?: string;
  asset_name?: string;
  due_date?: string;
  resolved_at?: string;
  closed_at?: string;
  resolution_notes?: string;
  resolution_time_minutes?: number;
  tags?: string[];
  attachments?: any[];
  custom_fields?: Record<string, any>;
  sla_due_date?: string;
  sla_breached: boolean;
  satisfaction_rating?: number;
  feedback_comment?: string;
  created_at: string;
  updated_at?: string;
}

export interface TicketComment {
  id: string;
  tenant_id: string;
  ticket_id: string;
  author_id?: string;
  author?: {
    first_name?: string;
    last_name?: string;
  };
  content: string;
  is_internal: boolean;
  attachments?: any[];
  created_at: string;
  updated_at?: string;
}

export interface TicketHistory {
  id: string;
  tenant_id: string;
  ticket_id: string;
  changed_by?: string;
  changed_by_name?: string;
  field_name: string;
  old_value?: string;
  new_value?: string;
  change_reason?: string;
  created_at: string;
}

export interface SupportCategory {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  icon?: string;
  color?: string;
  default_priority: TicketPriority;
  sla_response_hours: number;
  sla_resolution_hours: number;
  auto_assign_to?: string;
  auto_assign_department?: string;
  requires_approval: boolean;
  is_active: boolean;
  sort_order: number;
  created_at: string;
  updated_at?: string;
}

export interface KnowledgeBaseArticle {
  id: string;
  tenant_id: string;
  title: string;
  content: string;
  summary?: string;
  category_id?: string;
  tags?: string[];
  is_published: boolean;
  is_internal: boolean;
  author_id?: string;
  author_name?: string;
  view_count: number;
  helpful_count: number;
  not_helpful_count: number;
  created_at: string;
  updated_at?: string;
}

export interface SupportDashboardStats {
  total_tickets: number;
  open_tickets: number;
  in_progress_tickets: number;
  resolved_tickets: number;
  closed_tickets: number;
  overdue_tickets: number;
  avg_resolution_time_minutes?: number;
  tickets_by_category: Record<string, number>;
  tickets_by_priority: Record<string, number>;
  satisfaction_avg?: number;
}
