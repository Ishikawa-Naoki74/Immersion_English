-- Users table based on Django Users model
CREATE TABLE users (
  user_id TEXT PRIMARY KEY,
  user_name VARCHAR(15),
  user_icon TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Channel decks table based on Django Channeldecks model
CREATE TABLE channel_decks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  channel_id VARCHAR(100) UNIQUE NOT NULL,
  channel_title VARCHAR(100) NOT NULL,
  channel_icon_url TEXT,
  total_study_time INTEGER DEFAULT 0,
  total_new_cards INTEGER DEFAULT 0,
  total_learning_cards INTEGER DEFAULT 0,
  total_review_cards INTEGER DEFAULT 0,
  uploads_playlist_id VARCHAR(100),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Videos table based on Django Videos model
CREATE TABLE videos (
  video_id VARCHAR(100) PRIMARY KEY,
  channel_id VARCHAR(100) DEFAULT 'unknown',
  title TEXT,
  description TEXT,
  thumbnail_url TEXT,
  duration INTEGER,
  published_at TIMESTAMP WITH TIME ZONE,
  total_study_time INTEGER DEFAULT 0,
  total_new_cards INTEGER DEFAULT 0,
  total_learning_cards INTEGER DEFAULT 0,
  total_review_cards INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Subtitles table for storing subtitle data
CREATE TABLE subtitles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id VARCHAR(100) REFERENCES videos(video_id) ON DELETE CASCADE,
  language VARCHAR(10) NOT NULL,
  text TEXT NOT NULL,
  start_time FLOAT NOT NULL,
  end_time FLOAT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_videos_channel_id ON videos(channel_id);
CREATE INDEX idx_subtitles_video_id ON subtitles(video_id);
CREATE INDEX idx_subtitles_video_language ON subtitles(video_id, language);
CREATE INDEX idx_subtitles_time_range ON subtitles(video_id, language, start_time, end_time);

-- Add foreign key constraint for videos
ALTER TABLE videos ADD CONSTRAINT fk_videos_channel_id 
  FOREIGN KEY (channel_id) REFERENCES channel_decks(channel_id);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE channel_decks ENABLE ROW LEVEL SECURITY;
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE subtitles ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (you may want to restrict this based on your needs)
CREATE POLICY "Enable read access for all users" ON users FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON users FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON users FOR UPDATE USING (true);

CREATE POLICY "Enable read access for all users" ON channel_decks FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON channel_decks FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON channel_decks FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON channel_decks FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON videos FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON videos FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON videos FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON videos FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON subtitles FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON subtitles FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON subtitles FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON subtitles FOR DELETE USING (true);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subtitles_updated_at BEFORE UPDATE ON subtitles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();