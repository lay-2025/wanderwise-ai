import { NextRequest, NextResponse } from "next/server";

const protectedPaths = ["/", "/chat", "/learning"];
const authPaths = ["/login", "/register"];

export default function proxy(req: NextRequest) {
  const path = req.nextUrl.pathname;
  const hasToken = req.cookies.has("access_token");

  const isProtected = protectedPaths.some(
    (p) => path === p || path.startsWith(p + "/")
  );
  const isAuthPath = authPaths.includes(path);

  if (isProtected && !hasToken) {
    return NextResponse.redirect(new URL("/login", req.nextUrl));
  }

  if (isAuthPath && hasToken) {
    return NextResponse.redirect(new URL("/", req.nextUrl));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|.*\\.png$).*)"],
};
