#include <windows.h>
static int x=50,y=50,dx=6,dy=4;
LRESULT CALLBACK W(HWND h,UINT m,WPARAM w,LPARAM l){
  if(m==WM_TIMER){RECT r;GetClientRect(h,&r);x+=dx;y+=dy;if(x<0||x>r.right-40)dx=-dx;if(y<0||y>r.bottom-40)dy=-dy;InvalidateRect(h,0,TRUE);return 0;}
  if(m==WM_PAINT){PAINTSTRUCT p;HDC d=BeginPaint(h,&p);HBRUSH b=CreateSolidBrush(RGB(255,80,0));SelectObject(d,b);Ellipse(d,x,y,x+40,y+40);
    TextOutA(d,10,10,"Test game running under Wine!",29);DeleteObject(b);EndPaint(h,&p);return 0;}
  if(m==WM_DESTROY){PostQuitMessage(0);return 0;}
  return DefWindowProc(h,m,w,l);}
int WINAPI WinMain(HINSTANCE i,HINSTANCE p,LPSTR c,int s){
  WNDCLASSA wc={0};wc.lpfnWndProc=W;wc.hInstance=i;wc.lpszClassName="B";wc.hbrBackground=(HBRUSH)GetStockObject(WHITE_BRUSH);wc.hCursor=LoadCursor(0,IDC_ARROW);
  RegisterClassA(&wc);HWND h=CreateWindowA("B","Bounce Test",WS_OVERLAPPEDWINDOW|WS_VISIBLE,100,100,640,480,0,0,i,0);SetTimer(h,1,16,0);
  MSG m;while(GetMessage(&m,0,0,0)){TranslateMessage(&m);DispatchMessage(&m);}return 0;}
