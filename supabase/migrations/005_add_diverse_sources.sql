-- Add diverse AI news sources for better variety

INSERT INTO sources (name, url, type, category) VALUES
  -- Enterprise/Industry News
  ('TechCrunch AI', 'https://techcrunch.com/category/artificial-intelligence/feed/', 'rss', 'ecosystem'),
  ('VentureBeat AI', 'https://venturebeat.com/category/ai/feed/', 'rss', 'ecosystem'),
  ('Wired AI', 'https://www.wired.com/feed/tag/ai/latest/rss', 'rss', 'ecosystem'),
  ('Ars Technica Tech', 'https://feeds.arstechnica.com/arstechnica/technology-lab', 'rss', 'ecosystem'),
  ('MIT Technology Review', 'https://www.technologyreview.com/topic/artificial-intelligence/feed', 'rss', 'research'),

  -- Lab/Company Blogs
  ('Google AI Blog', 'https://blog.google/technology/ai/rss/', 'rss', 'lab'),
  ('Microsoft AI Blog', 'https://blogs.microsoft.com/ai/feed/', 'rss', 'lab'),
  ('NVIDIA AI Blog', 'https://blogs.nvidia.com/feed/', 'rss', 'lab'),

  -- Research/Academic
  ('Distill.pub', 'https://distill.pub/rss.xml', 'rss', 'research'),
  ('Towards Data Science', 'https://towardsdatascience.com/feed', 'rss', 'ecosystem'),
  ('Machine Learning Mastery', 'https://machinelearningmastery.com/feed/', 'rss', 'ecosystem'),

  -- Aggregators
  ('AI News', 'https://www.artificialintelligence-news.com/feed/', 'rss', 'ecosystem'),
  ('The Gradient', 'https://thegradient.pub/rss/', 'rss', 'research')
ON CONFLICT (url) DO NOTHING;
