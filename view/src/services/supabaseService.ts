import { supabase } from 'boot/supabase'
import { Database } from 'src/types/supabase'

type Tables = Database['public']['Tables']
type VideoRow = Tables['videos']['Row']
type ChannelRow = Tables['channel_decks']['Row']
type SubtitleRow = Tables['subtitles']['Row']

export class SupabaseService {
  // Videos
  static async getVideos(): Promise<VideoRow[]> {
    const { data, error } = await supabase
      .from('videos')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) {
      console.error('Error fetching videos:', error)
      throw error
    }

    return data || []
  }

  static async getVideoById(videoId: string): Promise<VideoRow | null> {
    const { data, error } = await supabase
      .from('videos')
      .select('*')
      .eq('video_id', videoId)
      .single()

    if (error) {
      console.error('Error fetching video:', error)
      return null
    }

    return data
  }

  static async insertVideo(video: Tables['videos']['Insert']): Promise<VideoRow | null> {
    const { data, error } = await supabase
      .from('videos')
      .insert(video)
      .select()
      .single()

    if (error) {
      console.error('Error inserting video:', error)
      throw error
    }

    return data
  }

  static async updateVideo(videoId: string, updates: Tables['videos']['Update']): Promise<VideoRow | null> {
    const { data, error } = await supabase
      .from('videos')
      .update(updates)
      .eq('video_id', videoId)
      .select()
      .single()

    if (error) {
      console.error('Error updating video:', error)
      throw error
    }

    return data
  }

  static async deleteVideo(videoId: string): Promise<boolean> {
    const { error } = await supabase
      .from('videos')
      .delete()
      .eq('video_id', videoId)

    if (error) {
      console.error('Error deleting video:', error)
      return false
    }

    return true
  }

  // Channels
  static async getChannels(): Promise<ChannelRow[]> {
    const { data, error } = await supabase
      .from('channel_decks')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) {
      console.error('Error fetching channels:', error)
      throw error
    }

    return data || []
  }

  static async getChannelById(channelId: string): Promise<ChannelRow | null> {
    const { data, error } = await supabase
      .from('channel_decks')
      .select('*')
      .eq('channel_id', channelId)
      .single()

    if (error) {
      console.error('Error fetching channel:', error)
      return null
    }

    return data
  }

  static async insertChannel(channel: Tables['channel_decks']['Insert']): Promise<ChannelRow | null> {
    const { data, error } = await supabase
      .from('channel_decks')
      .insert(channel)
      .select()
      .single()

    if (error) {
      console.error('Error inserting channel:', error)
      throw error
    }

    return data
  }

  // Subtitles
  static async getSubtitlesByVideoId(videoId: string, language?: string): Promise<SubtitleRow[]> {
    let query = supabase
      .from('subtitles')
      .select('*')
      .eq('video_id', videoId)
      .order('start_time', { ascending: true })

    if (language) {
      query = query.eq('language', language)
    }

    const { data, error } = await query

    if (error) {
      console.error('Error fetching subtitles:', error)
      throw error
    }

    return data || []
  }

  static async insertSubtitles(subtitles: Tables['subtitles']['Insert'][]): Promise<SubtitleRow[]> {
    const { data, error } = await supabase
      .from('subtitles')
      .insert(subtitles)
      .select()

    if (error) {
      console.error('Error inserting subtitles:', error)
      throw error
    }

    return data || []
  }

  static async getSubtitleAtTime(videoId: string, currentTime: number, language: string): Promise<SubtitleRow | null> {
    const { data, error } = await supabase
      .from('subtitles')
      .select('*')
      .eq('video_id', videoId)
      .eq('language', language)
      .lte('start_time', currentTime)
      .gte('end_time', currentTime)
      .single()

    if (error) {
      console.error('Error fetching subtitle at time:', error)
      return null
    }

    return data
  }

  // Real-time subscriptions
  static subscribeToVideos(callback: (payload: any) => void) {
    return supabase
      .channel('videos')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'videos' }, callback)
      .subscribe()
  }

  static subscribeToSubtitles(videoId: string, callback: (payload: any) => void) {
    return supabase
      .channel(`subtitles-${videoId}`)
      .on('postgres_changes', 
        { 
          event: '*', 
          schema: 'public', 
          table: 'subtitles',
          filter: `video_id=eq.${videoId}`
        }, 
        callback
      )
      .subscribe()
  }
}