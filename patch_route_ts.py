import sys

route_path = '/home/wangshuyue/litelanglearn_repo/dev/litelanglearn/frontend/app/api/[...slug]/route.ts'
with open(route_path, 'r') as f:
    content = f.read()

get_old = """export async function GET(req: NextRequest, { params }: { params: Promise<{ slug: string[] }> }) {
  const { slug } = await params;
  const path = slug.join('/');
  const searchParams = req.nextUrl.searchParams;
  
  let command = '';
  const data: Record<string, string> = {};"""

get_new = """export async function GET(req: NextRequest, { params }: { params: Promise<{ slug: string[] }> }) {
  const { slug } = await params;
  const path = slug.join('/');
  const searchParams = req.nextUrl.searchParams;
  
  let command = '';
  const data: Record<string, string> = {};
  
  // Handle Bot API Key Auth
  const authHeader = req.headers.get('authorization');
  if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      const userAgent = req.headers.get('user-agent') || 'Unknown';
      const authResult = await runPythonCommand<any>('validate_bot_api_key', { 
          api_key: token, 
          endpoint: path, 
          user_agent: userAgent 
      });
      if (authResult.error) {
          return NextResponse.json({ error: authResult.error }, { status: authResult.status_code || 401 });
      }
      if (authResult.valid) {
          data['user_email'] = authResult.user_email;
      }
  }"""

post_old = """export async function POST(req: NextRequest, { params }: { params: Promise<{ slug: string[] }> }) {
  const { slug } = await params;
  const path = slug.join('/');
  
  let command = '';
  let data: Record<string, unknown> = {};"""

post_new = """export async function POST(req: NextRequest, { params }: { params: Promise<{ slug: string[] }> }) {
  const { slug } = await params;
  const path = slug.join('/');
  
  let command = '';
  let data: Record<string, unknown> = {};
  
  // Handle Bot API Key Auth
  const authHeader = req.headers.get('authorization');
  if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      const userAgent = req.headers.get('user-agent') || 'Unknown';
      const authResult = await runPythonCommand<any>('validate_bot_api_key', { 
          api_key: token, 
          endpoint: path, 
          user_agent: userAgent 
      });
      if (authResult.error) {
          return NextResponse.json({ error: authResult.error }, { status: authResult.status_code || 401 });
      }
      if (authResult.valid) {
          data['user_email'] = authResult.user_email;
      }
  }"""

delete_old = """export async function DELETE(req: NextRequest, { params }: { params: Promise<{ slug: string[] }> }) {
  const { slug } = await params;
  const path = slug.join('/');
  
  let command = '';
  let data: Record<string, unknown> = {};"""

delete_new = """export async function DELETE(req: NextRequest, { params }: { params: Promise<{ slug: string[] }> }) {
  const { slug } = await params;
  const path = slug.join('/');
  
  let command = '';
  let data: Record<string, unknown> = {};
  
  // Handle Bot API Key Auth
  const authHeader = req.headers.get('authorization');
  if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      const userAgent = req.headers.get('user-agent') || 'Unknown';
      const authResult = await runPythonCommand<any>('validate_bot_api_key', { 
          api_key: token, 
          endpoint: path, 
          user_agent: userAgent 
      });
      if (authResult.error) {
          return NextResponse.json({ error: authResult.error }, { status: authResult.status_code || 401 });
      }
      if (authResult.valid) {
          data['user_email'] = authResult.user_email;
      }
  }"""

if get_old in content: content = content.replace(get_old, get_new)
if post_old in content: content = content.replace(post_old, post_new)
if delete_old in content: content = content.replace(delete_old, delete_new)

with open(route_path, 'w') as f:
    f.write(content)

print("Patched route.ts successfully.")
