// Supabase connection configuration

export const SUPABASE_CONFIG = {
  // Original provided URL had .cof instead of .co - fixing this
  url: 'https://uuwopjlfcfhldzpzvrah.supabase.co',
  anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1d29wamxmY2ZobGR6cHp2cmFoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI0NDk4OTAsImV4cCI6MjA2ODAyNTg5MH0.CXeHIPbDpOFPtPbCZJerV9Qg6Vt1uddjux96vGzuUxU',
  serviceRoleKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1d29wamxmY2ZobGR6cHp2cmFoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjQ0OTg5MCwiZXhwIjoyMDY4MDI1ODkwfQ.fk4_K5y6ET05shqQWDGJ6BmDEzE5MMcGPG9ykr7NzSkf'
}

// Validate configuration
export function validateSupabaseConfig() {
  const errors = []
  
  if (!SUPABASE_CONFIG.url) {
    errors.push('Supabase URL is missing')
  } else {
    try {
      new URL(SUPABASE_CONFIG.url)
    } catch (e) {
      errors.push('Supabase URL format is invalid')
    }
  }
  
  if (!SUPABASE_CONFIG.anonKey) {
    errors.push('Supabase anon key is missing')
  } else if (SUPABASE_CONFIG.anonKey.length < 100) {
    errors.push('Supabase anon key appears to be too short')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}