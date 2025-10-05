export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          email: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          email?: string
          created_at?: string
          updated_at?: string
        }
      }
      videos: {
        Row: {
          id: string
          video_id: string
          channel_id: string
          title: string
          description: string
          thumbnail_url: string
          duration: number
          published_at: string
          total_study_time: number
          total_new_cards: number
          total_learning_cards: number
          total_review_cards: number
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          video_id: string
          channel_id: string
          title: string
          description?: string
          thumbnail_url?: string
          duration?: number
          published_at?: string
          total_study_time?: number
          total_new_cards?: number
          total_learning_cards?: number
          total_review_cards?: number
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          video_id?: string
          channel_id?: string
          title?: string
          description?: string
          thumbnail_url?: string
          duration?: number
          published_at?: string
          total_study_time?: number
          total_new_cards?: number
          total_learning_cards?: number
          total_review_cards?: number
          created_at?: string
          updated_at?: string
        }
      }
      channel_decks: {
        Row: {
          id: string
          channel_id: string
          title: string
          description?: string
          thumbnail_url?: string
          subscriber_count?: number
          video_count?: number
          created_at: string
          updated_at?: string
        }
        Insert: {
          id?: string
          channel_id: string
          title: string
          description?: string
          thumbnail_url?: string
          subscriber_count?: number
          video_count?: number
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          channel_id?: string
          title?: string
          description?: string
          thumbnail_url?: string
          subscriber_count?: number
          video_count?: number
          created_at?: string
          updated_at?: string
        }
      }
      subtitles: {
        Row: {
          id: string
          video_id: string
          language: string
          text: string
          start_time: number
          end_time: number
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          video_id: string
          language: string
          text: string
          start_time: number
          end_time: number
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          video_id?: string
          language?: string
          text?: string
          start_time?: number
          end_time?: number
          created_at?: string
          updated_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}