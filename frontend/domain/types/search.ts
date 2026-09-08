export type SearchCategory = 
  | 'TRAIN' 
  | 'MAINTENANCE_TASK' 
  | 'ASSET' 
  | 'BLOCK' 
  | 'SECTION' 
  | 'INCIDENT' 
  | 'PLAN' 
  | 'RECOMMENDATION';

export interface SearchResultItem {
  id: string;
  title: string;
  subtitle: string;
  category: SearchCategory;
  url: string;
  statusTone?: 'neutral' | 'attention' | 'warning' | 'critical' | 'approved';
  badge?: string;
}
