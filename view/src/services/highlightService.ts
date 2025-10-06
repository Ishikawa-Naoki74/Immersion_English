import { api } from 'boot/axios';

export interface Highlight {
  id?: number;
  video_id: string;
  highlighted_text: string;
  timestamp: number;
  meaning_japanese?: string;
  etymology?: string;
  image_url?: string;
  created_at?: string;
  updated_at?: string;
}

export const HighlightService = {
  /**
   * ハイライトを作成（意味と語源を自動生成）
   */
  async createHighlight(data: {
    video_id: string;
    highlighted_text: string;
    timestamp: number;
    auto_generate?: boolean;
  }): Promise<Highlight> {
    const response = await api.post('/highlights/', {
      ...data,
      auto_generate: data.auto_generate !== false, // デフォルトtrue
    });
    return response.data;
  },

  /**
   * 動画のハイライト一覧を取得
   */
  async getHighlights(videoId: string): Promise<Highlight[]> {
    const response = await api.get('/highlights/', {
      params: { video_id: videoId },
    });
    return response.data;
  },

  /**
   * ハイライトの詳細を取得
   */
  async getHighlight(highlightId: number): Promise<Highlight> {
    const response = await api.get(`/highlights/${highlightId}/`);
    return response.data;
  },

  /**
   * ハイライトを更新
   */
  async updateHighlight(
    highlightId: number,
    data: Partial<Highlight>
  ): Promise<Highlight> {
    const response = await api.patch(`/highlights/${highlightId}/`, data);
    return response.data;
  },

  /**
   * ハイライトを削除
   */
  async deleteHighlight(highlightId: number): Promise<void> {
    await api.delete(`/highlights/${highlightId}/`);
  },
};
