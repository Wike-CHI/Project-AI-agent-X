# OAuth 2.0 认证架构设计

## 1. 认证流程设计

```
┌─────────────────────────────────────────────────────────────────┐
│                    OAuth 2.0 认证流程                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  用户                    客户端                  服务端          │
│    │                        │                       │           │
│    │  1. 打开登录页          │                       │           │
│    │───────────────────────>│                       │           │
│    │                        │  2. 重定向至认证页     │           │
│    │                        │───────────────────────>│           │
│    │                        │                       │           │
│    │  3. 用户授权           │                       │           │
│    │<───────────────────────│                       │           │
│    │                        │                       │           │
│    │                        │  4. 授权码回调         │           │
│    │                        │<───────────────────────│           │
│    │                        │                       │           │
│    │                        │  5. 交换 Token         │           │
│    │                        │───────────────────────>│           │
│    │                        │                       │           │
│    │                        │  6. 返回 Token         │           │
│    │                        │<───────────────────────│           │
│    │                        │                       │           │
│    │  7. 开始使用           │                       │           │
│    │───────────────────────>│                       │           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 2. OAuth 提供商配置

```python
# backend/src/pdns/config/oauth_config.py

from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from functools import lru_cache

class OAuthProvider(str, Enum):
    GOOGLE = "google"
    GITHUB = "github"
    SELF_HOSTED = "self_hosted"
    # 中国 OAuth 提供商
    WECHAT = "wechat"
    WECHAT_MP = "wechat_mp"
    ALIPAY = "alipay"
    QQ = "qq"
    DINGTALK = "dingtalk"

class OAuthConfig(BaseModel):
    """OAuth 配置模型"""
    provider: OAuthProvider
    client_id: str
    client_secret: str
    auth_url: str
    token_url: str
    userinfo_url: str
    scopes: List[str]
    redirect_uri: str = "http://localhost:3000/auth/callback"

# OAuth 提供商配置
OAUTH_CONFIGS = {
    OAuthProvider.GOOGLE: OAuthConfig(
        provider=OAuthProvider.GOOGLE,
        client_id="${GOOGLE_CLIENT_ID}",
        client_secret="${GOOGLE_CLIENT_SECRET}",
        auth_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        userinfo_url="https://www.googleapis.com/oauth2/v3/userinfo",
        scopes=["openid", "email", "profile"]
    ),
    OAuthProvider.GITHUB: OAuthConfig(
        provider=OAuthProvider.GITHUB,
        client_id="${GITHUB_CLIENT_ID}",
        client_secret="${GITHUB_CLIENT_SECRET}",
        auth_url="https://github.com/login/oauth/authorize",
        token_url="https://github.com/login/oauth/access_token",
        userinfo_url="https://api.github.com/user",
        scopes=["read:user", "user:email"]
    ),
    OAuthProvider.SELF_HOSTED: OAuthConfig(
        provider=OAuthProvider.SELF_HOSTED,
        client_id="${SELF_HOSTED_CLIENT_ID}",
        client_secret="${SELF_HOSTED_CLIENT_SECRET}",
        auth_url="https://auth.pdns.local/oauth/authorize",
        token_url="https://auth.pdns.local/oauth/token",
        userinfo_url="https://auth.pdns.local/userinfo",
        scopes=["openid", "profile", "email"]
    ),
    # ============ 中国 OAuth 提供商 ============
    OAuthProvider.WECHAT: OAuthConfig(
        provider=OAuthProvider.WECHAT,
        client_id="${WECHAT_APP_ID}",
        client_secret="${WECHAT_APP_SECRET}",
        auth_url="https://open.weixin.qq.com/connect/qrconnect",
        token_url="https://api.weixin.qq.com/sns/oauth2/access_token",
        userinfo_url="https://api.weixin.qq.com/sns/userinfo",
        scopes=["snsapi_login"],
        redirect_uri="http://localhost:3000/auth/callback/wechat"
    ),
    OAuthProvider.ALIPAY: OAuthConfig(
        provider=OAuthProvider.ALIPAY,
        client_id="${ALIPAY_APP_ID}",
        client_secret="${ALIPAY_APP_PRIVATE_KEY}",
        auth_url="https://openauth.alipay.com/oauth2/publicAppAuthorize.htm",
        token_url="https://openapi.alipay.com/gateway.do",
        userinfo_url="https://openapi.alipay.com/userinfo/share",
        scopes=["auth_user"],
        redirect_uri="http://localhost:3000/auth/callback/alipay"
    ),
    OAuthProvider.QQ: OAuthConfig(
        provider=OAuthProvider.QQ,
        client_id="${QQ_APP_ID}",
        client_secret="${QQ_APP_KEY}",
        auth_url="https://graph.qq.com/oauth2.0/authorize",
        token_url="https://graph.qq.com/oauth2.0/token",
        userinfo_url="https://graph.qq.com/user/get_user_info",
        scopes=["get_user_info"],
        redirect_uri="http://localhost:3000/auth/callback/qq"
    ),
    OAuthProvider.DINGTALK: OAuthConfig(
        provider=OAuthProvider.DINGTALK,
        client_id="${DINGTALK_APP_KEY}",
        client_secret="${DINGTALK_APP_SECRET}",
        auth_url="https://oapi.dingtalk.com/connect/qrconnect",
        token_url="https://oapi.dingtalk.com/sns/gettoken",
        userinfo_url="https://oapi.dingtalk.com/sns/getuserinfo",
        scopes=["snsapi"],
        redirect_uri="http://localhost:3000/auth/callback/dingtalk"
    )
}

# 自建 OAuth 配置（可选）
SELF_HOSTED_OAUTH = {
    "enabled": True,
    "issuer": "https://auth.pdns.local",
    "jwks_uri": "https://auth.pdns.local/.well-known/jwks.json"
}
```

## 3. Token 管理

```python
# backend/src/pdns/security/token_manager.py

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from uuid import uuid4
import secrets

class TokenConfig:
    """Token 配置"""
    ACCESS_TOKEN_LIFETIME = timedelta(hours=1)      # 1小时
    REFRESH_TOKEN_LIFETIME = timedelta(days=7)      # 7天
    REFRESH_TOKEN_ROTATION = True                   # 刷新后旧Token失效
    ALGORITHM = "HS256"
    SECRET_KEY = "${JWT_SECRET_KEY}"  # 生产环境使用环境变量

class TokenManager:
    """Token 管理器"""

    def __init__(self, config: TokenConfig = None):
        self.config = config or TokenConfig()
        self._blacklisted_tokens = set()  # Token 黑名单（生产环境用 Redis）
        self._refresh_token_store = {}    # 刷新Token存储（生产环境用 Redis）

    def create_access_token(
        self,
        user_id: str,
        additional_claims: dict = None
    ) -> str:
        """创建访问 Token"""
        expire = datetime.utcnow() + self.config.ACCESS_TOKEN_LIFETIME

        payload = {
            "sub": user_id,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": str(uuid4())
        }

        if additional_claims:
            payload.update(additional_claims)

        return jwt.encode(
            payload,
            self.config.SECRET_KEY,
            algorithm=self.config.ALGORITHM
        )

    def create_refresh_token(self, user_id: str) -> str:
        """创建刷新 Token"""
        expire = datetime.utcnow() + self.config.REFRESH_TOKEN_LIFETIME
        token_id = str(uuid4())

        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": token_id
        }

        refresh_token = jwt.encode(
            payload,
            self.config.SECRET_KEY,
            algorithm=self.config.ALGORITHM
        )

        # 存储刷新 Token（用于撤销）
        self._refresh_token_store[token_id] = {
            "user_id": user_id,
            "revoked": False
        }

        return refresh_token

    def create_token_pair(self, user_id: str) -> dict:
        """创建 Token 对"""
        return {
            "access_token": self.create_access_token(user_id),
            "refresh_token": self.create_refresh_token(user_id),
            "token_type": "Bearer",
            "expires_in": int(self.config.ACCESS_TOKEN_LIFETIME.total_seconds())
        }

    def verify_access_token(self, token: str) -> Optional[dict]:
        """验证访问 Token"""
        try:
            payload = jwt.decode(
                token,
                self.config.SECRET_KEY,
                algorithms=[self.config.ALGORITHM]
            )

            if payload.get("type") != "access":
                return None

            if payload["jti"] in self._blacklisted_tokens:
                return None

            return payload

        except JWTError:
            return None

    def refresh_tokens(self, refresh_token: str) -> Optional[dict]:
        """使用刷新 Token 获取新的 Token 对"""
        try:
            payload = jwt.decode(
                refresh_token,
                self.config.SECRET_KEY,
                algorithms=[self.config.ALGORITHM]
            )

            if payload.get("type") != "refresh":
                return None

            token_id = payload.get("jti")
            stored = self._refresh_token_store.get(token_id)

            if not stored or stored.get("revoked"):
                return None

            user_id = payload["sub"]

            # 如果启用了 Token 轮转，撤销旧 Token
            if self.config.REFRESH_TOKEN_ROTATION:
                stored["revoked"] = True

            return self.create_token_pair(user_id)

        except JWTError:
            return None

    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """撤销刷新 Token"""
        try:
            payload = jwt.decode(
                refresh_token,
                self.config.SECRET_KEY,
                algorithms=[self.config.ALGORITHM]
            )

            token_id = payload.get("jti")
            if token_id in self._refresh_token_store:
                self._refresh_token_store[token_id]["revoked"] = True
                return True

            return False

        except JWTError:
            return False

    def blacklist_token(self, token: str):
        """将 Token 加入黑名单（用于登出）"""
        try:
            payload = jwt.decode(
                token,
                self.config.SECRET_KEY,
                algorithms=[self.config.ALGORITHM],
                options={"verify_exp": False}
            )
            self._blacklisted_tokens.add(payload["jti"])
        except JWTError:
            pass
```

## 4. OAuth 服务实现

```python
# backend/src/pdns/api/oauth_service.py

from typing import Optional
from requests import get, post
from json import loads as json_loads
from urllib.parse import urlencode, urlparse
import secrets

class OAuthService:
    """OAuth 服务"""

    def __init__(self, oauth_configs, token_manager):
        self.configs = oauth_configs
        self.token_manager = token_manager
        self._state_store = {}  # 生产环境用 Redis

    def get_authorization_url(self, provider: str, state: str = None) -> str:
        """获取授权 URL"""
        config = self.configs.get(provider)
        if not config:
            raise ValueError(f"Unknown OAuth provider: {provider}")

        # 生成并存储 state（防止 CSRF）
        if not state:
            state = secrets.token_urlsafe(32)
            self._state_store[state] = {"provider": provider}

        params = {
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "response_type": "code",
            "scope": " ".join(config.scopes),
            "state": state
        }

        return f"{config.auth_url}?{urlencode(params)}"

    async def handle_callback(
        self,
        provider: str,
        code: str,
        state: str
    ) -> dict:
        """处理 OAuth 回调"""
        # 验证 state
        if state not in self._state_store:
            raise ValueError("Invalid state parameter")

        stored_state = self._state_store.pop(state)
        if stored_state.get("provider") != provider:
            raise ValueError("Provider mismatch")

        config = self.configs.get(provider)
        if not config:
            raise ValueError(f"Unknown OAuth provider: {provider}")

        # 1. 交换授权码获取 Token
        token_data = await self._exchange_code_for_token(provider, code, config)

        # 2. 获取用户信息
        user_info = await self._get_user_info(provider, token_data["access_token"], config)

        # 3. 创建本地用户或更新现有用户
        user = await self._find_or_create_user(provider, user_info)

        # 4. 生成应用 Token
        tokens = self.token_manager.create_token_pair(str(user.id))

        return {
            "user": user.to_dict(),
            **tokens
        }

    async def _exchange_code_for_token(
        self,
        provider: str,
        code: str,
        config
    ) -> dict:
        """交换授权码获取 Token"""
        response = post(
            config.token_url,
            data={
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "code": code,
                "redirect_uri": config.redirect_uri,
                "grant_type": "authorization_code"
            },
            headers={"Accept": "application/json"}
        )

        if not response.ok:
            raise RuntimeError(f"Token exchange failed: {response.text}")

        return response.json()

    async def _get_user_info(
        self,
        provider: str,
        access_token: str,
        config
    ) -> dict:
        """获取用户信息"""
        response = get(
            config.userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if not response.ok:
            raise RuntimeError(f"Failed to get user info: {response.text}")

        return response.json()

    async def _find_or_create_user(self, provider: str, user_info: dict) -> User:
        """查找或创建用户"""
        # 实现用户查找/创建逻辑
        pass
```

## 5. API 路由

```python
# backend/src/pdns/api/routes/auth.py

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from typing import Optional

router = APIRouter(prefix="/auth", tags=["认证"])

@router.get("/login/{provider}")
async def login(
    provider: str,
    request: Request,
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """发起 OAuth 登录"""
    try:
        auth_url = oauth_service.get_authorization_url(provider)
        return RedirectResponse(url=auth_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/callback")
async def oauth_callback(
    provider: str,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """OAuth 回调处理"""
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    try:
        result = await oauth_service.handle_callback(provider, code, state)
        # 返回 Token（前端应该重定向到回调页面存储 Token）
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    token_manager: TokenManager = Depends(get_token_manager)
):
    """刷新 Token"""
    new_tokens = token_manager.refresh_tokens(refresh_token)

    if not new_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    return new_tokens

@router.post("/logout")
async def logout(
    request: Request,
    token_manager: TokenManager = Depends(get_token_manager)
):
    """登出"""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token_manager.blacklist_token(auth_header[7:])

    return {"message": "Logged out successfully"}
```

## 6. 环境变量配置

```bash
# .env.example - OAuth 配置

# OAuth 提供商配置
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# 自建 OAuth（可选）
SELF_HOSTED_CLIENT_ID=your_client_id
SELF_HOSTED_CLIENT_SECRET=your_client_secret
SELF_HOSTED_AUTH_URL=https://auth.pdns.local/oauth/authorize
SELF_HOSTED_TOKEN_URL=https://auth.pdns.local/oauth/token
SELF_HOSTED_USERINFO_URL=https://auth.pdns.local/userinfo

# JWT 配置（生产环境使用强密钥）
JWT_SECRET_KEY=your_super_secret_jwt_key_change_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# 重定向 URI
OAUTH_REDIRECT_URI=http://localhost:3000/auth/callback
```

## 7. 中国 OAuth 认证方案

### 7.1 中国 OAuth 提供商概述

由于国际 OAuth 服务（Google、GitHub）在中国访问受限，建议支持以下本土 OAuth 提供商：

| 提供商 | 使用场景 | 覆盖率 | 申请难度 | 适用用户群 |
|-------|---------|-------|---------|----------|
| **微信** | 个人用户首选 | 几乎人人都有 | 中） | 普通（需企业认证消费者 |
| **支付宝** | 支付相关场景 | 用户基数大 | 中（需企业认证） | 支付用户 |
| **QQ** | 年轻用户群体 | 80/90后常用 | 低（个人可申请） | 年轻用户 |
| **钉钉** | 企业场景 | 职场用户 | 中（需企业认证） | 企业用户 |

**推荐配置**：
```python
# 推荐的中国 OAuth 提供商列表
RECOMMENDED_CN_PROVIDERS = ["wechat", "alipay", "qq"]
```

### 7.2 微信 OAuth 详细实现

#### 7.2.1 微信登录流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    微信扫码登录流程                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  用户                    前端                     服务端          │
│    │                        │                       │           │
│    │  1. 点击"微信登录"     │                       │           │
│    │───────────────────────>│                       │           │
│    │                        │                       │           │
│    │                        │  2. 请求授权码         │           │
│    │                        │───────────────────────>│           │
│    │                        │                       │           │
│    │                        │  3. 返回授权码         │           │
│    │                        │<───────────────────────│           │
│    │                        │                       │           │
│    │  4. 显示二维码          │                       │           │
│    │<───────────────────────│                       │           │
│    │                        │                       │           │
│    │  5. 用户手机扫码确认    │                       │           │
│    │                        │                       │           │
│    │                        │  6. 微信回调授权码     │           │
│    │                        │<───────────────────────│           │
│    │                        │                       │           │
│    │                        │  7. 换取 Access Token │           │
│    │                        │───────────────────────>│           │
│    │                        │                       │           │
│    │                        │  8. 获取用户信息       │           │
│    │                        │───────────────────────>│           │
│    │                        │                       │           │
│    │                        │  9. 返回登录结果       │           │
│    │                        │<───────────────────────│           │
│    │  10. 登录成功           │                       │           │
│    │<───────────────────────│                       │           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 7.2.2 微信 OAuth 服务实现

```python
# backend/src/pdns/api/oauth/wechat_service.py

from typing import Optional, Dict, Any
from urllib.parse import urlencode
import httpx

WECHAT_API_BASE = "https://api.weixin.qq.com"

class WeChatOAuthService:
    """微信 OAuth 服务"""

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret

    def get_authorization_url(
        self,
        redirect_uri: str,
        state: str = None,
        style: str = "black",
        href: str = None
    ) -> str:
        """
        获取微信授权 URL

        参数:
            redirect_uri: 回调地址（需 URL 编码）
            state: 状态参数，用于防止 CSRF
            style: 二维码样式（black/white）
            href: 自定义二维码样式 URL
        """
        params = {
            "appid": self.app_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "snsapi_login",
            "state": state or self._generate_state()
        }

        if style:
            params["style"] = style

        if href:
            params["href"] = href

        return f"{WECHAT_API_BASE}/connect/qrconnect?{urlencode(params)}"

    async def handle_callback(self, code: str) -> Dict[str, Any]:
        """
        处理微信回调

        返回: {
            "openid": "用户唯一标识",
            "access_token": "访问令牌",
            "refresh_token": "刷新令牌",
            "expires_in": 7200,
            "unionid": "用户在开放平台的唯一标识符"
        }
        """
        # 1. 用 code 换取 access_token
        token_url = f"{WECHAT_API_BASE}/sns/oauth2/access_token"
        params = {
            "appid": self.app_id,
            "secret": self.app_secret,
            "code": code,
            "grant_type": "authorization_code"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(token_url, params=params)
            token_data = response.json()

        if "errcode" in token_data and token_data["errcode"] != 0:
            raise RuntimeError(f"微信 Token 错误: {token_data['errmsg']}")

        # 2. 获取用户信息
        user_info = await self._get_user_info(
            token_data["access_token"],
            token_data["openid"]
        )

        return {
            "provider": "wechat",
            "openid": token_data["openid"],
            "unionid": token_data.get("unionid"),
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expires_in": token_data.get("expires_in", 7200),
            "user_info": user_info
        }

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """刷新 access_token"""
        url = f"{WECHAT_API_BASE}/sns/oauth2/refresh_token"
        params = {
            "appid": self.app_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

        if "errcode" in data and data["errcode"] != 0:
            raise RuntimeError(f"微信 Token 刷新错误: {data['errmsg']}")

        return data

    async def _get_user_info(
        self,
        access_token: str,
        openid: str
    ) -> Dict[str, Any]:
        """获取用户基本信息"""
        url = f"{WECHAT_API_BASE}/sns/userinfo"
        params = {
            "access_token": access_token,
            "openid": openid,
            "lang": "zh_CN"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

        if "errcode" in data and data["errcode"] != 0:
            raise RuntimeError(f"获取用户信息错误: {data['errmsg']}")

        return {
            "openid": data.get("openid"),
            "nickname": data.get("nickname"),
            "sex": data.get("sex"),
            "province": data.get("province"),
            "city": data.get("city"),
            "country": data.get("country"),
            "headimgurl": data.get("headimgurl"),
            "privilege": data.get("privilege", []),
            "unionid": data.get("unionid")
        }

    def _generate_state(self) -> str:
        """生成随机 state"""
        import hashlib
        import time
        return hashlib.md5(f"{time.time()}-{self.app_id}".encode()).hexdigest()
```

#### 7.2.3 微信联合登录注意事项

```python
# 微信联合登录注意事项

WECHAT_NOTES = """
1. UnionID 机制：
   - 同一个用户在不同应用（公众号、小程序、App）中的 OpenID 不同
   - UnionID 是用户在开放平台的唯一标识
   - 需要在微信开放平台绑定多个应用才能获取 UnionID

2. Access Token：
   - 有效期为 2 小时（7200秒）
   - 需要主动刷新，不能依赖过期时间
   - 有效期内重复获取会返回相同的 Token

3. 用户信息：
   - 昵称可能包含特殊字符，需做好转义处理
   - 头像 URL 可能失效，需做好降级处理
   - 性别：1=男，2=女，0=未知

4. 报错处理：
   - errcode=40029: code 无效或已使用
   - errcode=40163: code 已被使用
   - errcode=40013: appid 无效
"""
```

### 7.3 支付宝 OAuth 详细实现

#### 7.3.1 支付宝 OAuth 特点

```python
# backend/src/pdns/api/oauth/alipay_service.py

from typing import Dict, Any
from urllib.parse import urlencode
import httpx
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

class AlipayOAuthService:
    """支付宝 OAuth 服务"""

    def __init__(
        self,
        app_id: str,
        private_key: str,
        alipay_public_key: str
    ):
        self.app_id = app_id
        self.private_key = private_key
        self.alipay_public_key = alipay_public_key
        self.api_base = "https://openapi.alipay.com/gateway.do"

    def get_authorization_url(
        self,
        redirect_uri: str,
        state: str = None
    ) -> str:
        """
        获取支付宝授权 URL

        支付宝使用 app_auth_code 方式进行授权
        """
        params = {
            "app_id": self.app_id,
            "method": "alipay.system.oauth.token",
            "charset": "UTF-8",
            "sign_type": "RSA2",
            "timestamp": self._get_timestamp(),
            "version": "1.0",
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }

        # 注意：支付宝授权需要先获取 app_auth_code
        # 这里返回的是授权页面 URL
        auth_url = (
            f"https://openauth.alipay.com/oauth2/publicAppAuthorize.htm?"
            f"app_id={self.app_id}&"
            f"redirect_uri={urlencode(redirect_uri)}&"
            f"scope=auth_user&"
            f"state={state or ''}"
        )

        return auth_url

    async def handle_callback(
        self,
        code: str,
        auth_token: str = None
    ) -> Dict[str, Any]:
        """处理支付宝回调"""
        # 支付宝使用 system.oauth.token 接口
        params = {
            "app_id": self.app_id,
            "method": "alipay.system.oauth.token",
            "charset": "UTF-8",
            "sign_type": "RSA2",
            "timestamp": self._get_timestamp(),
            "version": "1.0",
            "grant_type": "authorization_code",
            "code": code
        }

        # 签名
        sign_string = self._build_sign_string(params)
        sign = self._sign(sign_string)

        params["sign"] = sign

        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_base, data=params)
            result = response.json()

        # 解析响应
        token_response = result.get("alipay_system_oauth_token_response", {})

        return {
            "provider": "alipay",
            "user_id": token_response.get("user_id"),
            "access_token": token_response.get("access_token"),
            "refresh_token": token_response.get("refresh_token"),
            "expires_in": token_response.get("expires_in"),
            "re_expires_in": token_response.get("re_expires_in"),
            "user_info": {
                "nick_name": token_response.get("nick_name"),
                "avatar": token_response.get("avatar")
            }
        }

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """获取用户信息"""
        params = {
            "app_id": self.app_id,
            "method": "alipay.user.info.share",
            "charset": "UTF-8",
            "sign_type": "RSA2",
            "timestamp": self._get_timestamp(),
            "version": "1.0",
            "auth_token": access_token
        }

        sign_string = self._build_sign_string(params)
        sign = self._sign(sign_string)
        params["sign"] = sign

        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_base, data=params)
            result = response.json()

        user_info = result.get("alipay_user_info_share_response", {})

        return {
            "user_id": user_info.get("user_id"),
            "nick_name": user_info.get("nick_name"),
            "avatar": user_info.get("avatar"),
            "gender": user_info.get("gender"),
            "province": user_info.get("province"),
            "city": user_info.get("city")
        }

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _build_sign_string(self, params: dict) -> str:
        """构建签名字符串"""
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        return "&".join([f"{k}={v}" for k, v in sorted_params if v])

    def _sign(self, sign_string: str) -> str:
        """RSA2 签名"""
        private_key = serialization.load_pem_private_key(
            self.private_key.encode(),
            password=None,
            backend=default_backend()
        )

        signature = private_key.sign(
            sign_string.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        return base64.b64encode(signature).decode()
```

### 7.4 QQ OAuth 详细实现

```python
# backend/src/pdns/api/oauth/qq_service.py

from typing import Dict, Any
from urllib.parse import urlencode
import httpx

QQ_API_BASE = "https://graph.qq.com"

class QQOAuthService:
    """QQ OAuth 服务"""

    def __init__(self, app_id: str, app_key: str):
        self.app_id = app_id
        self.app_key = app_key

    def get_authorization_url(
        self,
        redirect_uri: str,
        state: str = None
    ) -> str:
        """获取 QQ 授权 URL"""
        params = {
            "client_id": self.app_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": "get_user_info",
            "state": state or self._generate_state()
        }

        return f"{QQ_API_BASE}/oauth2.0/authorize?{urlencode(params)}"

    async def handle_callback(self, code: str) -> Dict[str, Any]:
        """处理 QQ 回调"""
        # 1. 获取 access_token
        token_url = f"{QQ_API_BASE}/oauth2.0/token"
        params = {
            "grant_type": "authorization_code",
            "client_id": self.app_id,
            "client_secret": self.app_key,
            "code": code,
            "redirect_uri": ""  # 回调地址已在校验时使用
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(token_url, params=params)
            token_data = self._parse_response(response.text)

        if "error" in token_data:
            raise RuntimeError(f"QQ Token 错误: {token_data.get('error_description')}")

        # 2. 获取 openid
        openid_data = await self._get_openid(token_data["access_token"])

        # 3. 获取用户信息
        user_info = await self._get_user_info(
            token_data["access_token"],
            openid_data["openid"]
        )

        return {
            "provider": "qq",
            "openid": openid_data["openid"],
            "client_id": openid_data["client_id"],
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expires_in": token_data.get("expires_in"),
            "user_info": user_info
        }

    async def _get_openid(self, access_token: str) -> Dict[str, str]:
        """获取用户 OpenID"""
        url = f"{QQ_API_BASE}/oauth2.0/me"
        params = {"access_token": access_token}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

        # 返回格式: callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} );
        import re
        match = re.search(r'callback\(\s*(\{[^}]+\})\s*\);', response.text)
        if match:
            import json
            return json.loads(match.group(1))

        raise RuntimeError("获取 OpenID 失败")

    async def _get_user_info(
        self,
        access_token: str,
        openid: str
    ) -> Dict[str, Any]:
        """获取用户信息"""
        url = f"{QQ_API_BASE}/user/get_user_info"
        params = {
            "access_token": access_token,
            "oauth_consumer_key": self.app_id,
            "openid": openid
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

        if data.get("ret") != 0:
            raise RuntimeError(f"获取用户信息错误: {data.get('msg')}")

        return {
            "nickname": data.get("nickname"),
            "gender": data.get("gender"),
            "province": data.get("province"),
            "city": data.get("city"),
            "figureurl": data.get("figureurl"),
            "figureurl_1": data.get("figureurl_1"),
            "figureurl_2": data.get("figureurl_2")
        }

    def _parse_response(self, response: str) -> Dict[str, str]:
        """解析 URL 编码的响应"""
        result = {}
        for pair in response.split("&"):
            if "=" in pair:
                key, value = pair.split("=", 1)
                result[key] = value
        return result

    def _generate_state(self) -> str:
        """生成随机 state"""
        import hashlib
        import time
        return hashlib.md5(f"{time.time()}-{self.app_id}".encode()).hexdigest()
```

### 7.5 钉钉 OAuth 详细实现

```python
# backend/src/pdns/api/oauth/dingtalk_service.py

from typing import Dict, Any
from urllib.parse import urlencode
import httpx

DINGTALK_API_BASE = "https://oapi.dingtalk.com"

class DingTalkOAuthService:
    """钉钉 OAuth 服务"""

    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self._access_token = None
        self._token_expires_at = None

    def get_authorization_url(
        self,
        redirect_uri: str,
        state: str = None
    ) -> str:
        """获取钉钉授权 URL"""
        params = {
            "appkey": self.app_key,
            "response_type": "code",
            "scope": "snsapi",
            "redirect_uri": redirect_uri,
            "state": state or self._generate_state()
        }

        return f"{DINGTALK_API_BASE}/connect/qrconnect?{urlencode(params)}"

    async def handle_callback(
        self,
        code: str,
        tmp_auth_code: str = None
    ) -> Dict[str, Any]:
        """处理钉钉回调"""
        # 1. 获取 access_token（应用级别的）
        await self._ensure_app_token()

        # 2. 使用 tmp_auth_code 获取用户信息
        # 钉钉的回调会返回 tmp_auth_code，需要用它换取用户信息
        user_info = await self._get_user_info(tmp_auth_code or code)

        return {
            "provider": "dingtalk",
            "user_id": user_info.get("user_id"),
            "unionid": user_info.get("unionid"),
            "nickname": user_info.get("nickname"),
            "avatar": user_info.get("avatar"),
            "access_token": self._access_token,
            "user_info": user_info
        }

    async def _ensure_app_token(self):
        """确保应用 access_token 有效"""
        import time

        if (
            self._access_token and
            self._token_expires_at and
            time.time() < self._token_expires_at - 60
        ):
            return

        url = f"{DINGTALK_API_BASE}/gettoken"
        params = {
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

        if data.get("errcode") != 0:
            raise RuntimeError(f"获取钉钉 Token 错误: {data.get('errmsg')}")

        self._access_token = data["access_token"]
        # 钉钉 access_token 有效期为 2 小时
        self._token_expires_at = time.time() + data.get("expires_in", 7200) - 60

    async def _get_user_info(self, tmp_auth_code: str) -> Dict[str, Any]:
        """获取用户信息"""
        await self._ensure_app_token()

        url = f"{DINGTALK_API_BASE}/sns/getuserinfo"
        params = {
            "access_token": self._access_token,
            "tmp_auth_code": tmp_auth_code
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

        if data.get("errcode") != 0:
            raise RuntimeError(f"获取用户信息错误: {data.get('errmsg')}")

        user_info = data.get("user_info", {})

        return {
            "user_id": user_info.get("userid"),
            "unionid": user_info.get("unionid"),
            "nickname": user_info.get("nick"),
            "avatar": user_info.get("avatar"),
            "email": user_info.get("email"),
            "mobile": user_info.get("mobile")
        }

    def _generate_state(self) -> str:
        """生成随机 state"""
        import hashlib
        import time
        return hashlib.md5(f"{time.time()}-{self.app_key}".encode()).hexdigest()
```

### 7.6 前端适配方案

#### 7.6.1 微信扫码登录组件

```typescript
// frontend/src/components/auth/WeChatLoginButton.tsx

import React, { useEffect, useRef, useState } from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet } from 'react-native';

interface WeChatLoginButtonProps {
  onSuccess: (userInfo: any) => void;
  onError: (error: string) => void;
}

export const WeChatLoginButton: React.FC<WeChatLoginButtonProps> = ({
  onSuccess,
  onError
}) => {
  const [qrCode, setQrCode] = useState<string | null>(null);
  const [polling, setPolling] = useState(false);
  const pollTimerRef = useRef<NodeJS.Timeout | null>(null);

  // 生成微信登录二维码 URL
  const getQrCodeUrl = () => {
    const params = new URLSearchParams({
      appid: WECHAT_APP_ID,
      redirect_uri: encodeURIComponent(CALLBACK_URL),
      response_type: 'code',
      scope: 'snsapi_login',
      state: generateState()
    });
    return `https://open.weixin.qq.com/connect/qrconnect?${params.toString()}`;
  };

  // 轮询检查登录状态
  const startPolling = (state: string) => {
    setPolling(true);
    const checkLogin = async () => {
      try {
        const response = await fetch(`/api/auth/wechat/check?state=${state}`);
        const data = await response.json();

        if (data.status === 'confirmed') {
          stopPolling();
          onSuccess(data.userInfo);
        } else if (data.status === 'timeout') {
          stopPolling();
          onError('二维码已过期，请重试');
        }
      } catch (error) {
        console.error('轮询错误:', error);
      }
    };

    pollTimerRef.current = setInterval(checkLogin, 2000);
  };

  const stopPolling = () => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }
    setPolling(false);
  };

  const handlePress = () => {
    const state = generateState();
    setQrCode(getQrCodeUrl());
    startPolling(state);
  };

  useEffect(() => {
    return () => stopPolling();
  }, []);

  return (
    <TouchableOpacity style={styles.button} onPress={handlePress}>
      <View style={styles.iconContainer}>
        <Text style={styles.iconText}>微信</Text>
      </View>
      <Text style={styles.text}>微信登录</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#07C160',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8
  },
  iconContainer: {
    marginRight: 10
  },
  iconText: {
    color: '#fff',
    fontSize: 16
  },
  text: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600'
  }
});

// 辅助函数
function generateState(): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < 32; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}
```

#### 7.6.2 登录组件面板

```typescript
// frontend/src/screens/AuthScreen.tsx

import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { WeChatLoginButton } from '../components/auth/WeChatLoginButton';
import { GitHubLoginButton } from '../components/auth/GitHubLoginButton';

export const AuthScreen: React.FC = () => {
  const handleOAuthSuccess = async (userInfo: any) => {
    // 保存用户信息
    await saveUserToStore(userInfo);
    // 跳转到首页
    navigation.navigate('Home');
  };

  const handleOAuthError = (error: string) => {
    showToast(error);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.logoContainer}>
        <Text style={styles.title}>PDNS</Text>
        <Text style={styles.subtitle}>个人数字神经系统</Text>
      </View>

      <View style={styles.buttonContainer}>
        {/* 微信登录 - 中国用户首选 */}
        <WeChatLoginButton
          onSuccess={handleOAuthSuccess}
          onError={handleOAuthError}
        />

        {/* 支付宝登录 */}
        <TouchableOpacity
          style={[styles.button, styles.alipayButton]}
          onPress={() => navigation.navigate('AlipayAuth')}
        >
          <Text style={styles.buttonText}>支付宝登录</Text>
        </TouchableOpacity>

        {/* QQ 登录 */}
        <TouchableOpacity
          style={[styles.button, styles.qqButton]}
          onPress={() => navigation.navigate('QQAuth')}
        >
          <Text style={styles.buttonText}>QQ 登录</Text>
        </TouchableOpacity>

        <View style={styles.divider}>
          <View style={styles.line} />
          <Text style={styles.dividerText}>其他方式</Text>
          <View style={styles.line} />
        </View>

        {/* GitHub 登录 - 开发者首选 */}
        <GitHubLoginButton
          onSuccess={handleOAuthSuccess}
          onError={handleOAuthError}
        />
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1E1E1E',
    padding: 20
  },
  logoContainer: {
    alignItems: 'center',
    marginTop: 80,
    marginBottom: 60
  },
  title: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#6366F1'
  },
  subtitle: {
    fontSize: 16,
    color: '#888',
    marginTop: 10
  },
  buttonContainer: {
    gap: 15
  },
  button: {
    paddingVertical: 15,
    borderRadius: 10,
    alignItems: 'center'
  },
  alipayButton: {
    backgroundColor: '#1677FF'
  },
  qqButton: {
    backgroundColor: '#12B7F5'
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600'
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 20
  },
  line: {
    flex: 1,
    height: 1,
    backgroundColor: '#333'
  },
  dividerText: {
    marginHorizontal: 15,
    color: '#666'
  }
});
```

### 7.7 中国 OAuth 环境变量配置

```bash
# .env.example - 中国 OAuth 配置

# ============ 微信 OAuth ============
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret
WECHAT_REDIRECT_URI=http://localhost:3000/auth/callback/wechat
# 微信开放平台 appsecret（用于获取 UnionID）
WECHAT_OPEN_PLATFORM_APP_SECRET=your_open_platform_secret

# ============ 支付宝 OAuth ============
ALIPAY_APP_ID=your_alipay_app_id
ALIPAY_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\nYour Private Key Here\n-----END RSA PRIVATE KEY-----"
ALIPAY_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\nAlipay Public Key Here\n-----END PUBLIC KEY-----"
ALIPAY_REDIRECT_URI=http://localhost:3000/auth/callback/alipay

# ============ QQ OAuth ============
QQ_APP_ID=your_qq_app_id
QQ_APP_KEY=your_qq_app_key
QQ_REDIRECT_URI=http://localhost:3000/auth/callback/qq

# ============ 钉钉 OAuth ============
DINGTALK_APP_KEY=your_dingtalk_app_key
DINGTALK_APP_SECRET=your_dingtalk_app_secret
DINGTALK_REDIRECT_URI=http://localhost:3000/auth/callback/dingtalk

# ============ 回调路由配置 ============
# 微信回调路由（前端）
WECHAT_CALLBACK_URL=http://localhost:3000/auth/wechat/callback

# 支付宝回调路由（前端）
ALIPAY_CALLBACK_URL=http://localhost:3000/auth/alipay/callback
```

### 7.8 申请注意事项

#### 7.8.1 微信开放平台申请

```markdown
## 微信开放平台账号申请

1. **注册开放平台账号**
   - 访问 https://open.weixin.qq.com
   - 完成开发者认证（需缴纳 300 元认证费）

2. **创建网站应用**
   - 提交应用名称、简介、图标
   - 填写网站备案信息
   - 下载并部署 OAuth 授权回调域名的验证文件

3. **获取凭证**
   - AppID：应用唯一标识
   - AppSecret：应用密钥（需妥善保管）

4. **获取 UnionID**
   - 需在开放平台绑定公众号、小程序、App
   - 绑定后可通过 UnionID 识别同一用户
```

#### 7.8.2 支付宝开放平台申请

```markdown
## 支付宝开放平台账号申请

1. **注册开放平台账号**
   - 访问 https://open.alipay.com
   - 完成企业实名认证

2. **创建应用**
   - 选择"网页&移动应用"
   - 填写应用名称、图标、简介

3. **配置密钥**
   - 生成 RSA2 密钥对
   - 上传公钥到支付宝
   - 保存私钥（需妥善保管）

4. **添加能力**
   - 搜索"获取会员信息"
   - 添加到应用中
```

### 7.9 推荐的 OAuth 提供商配置

```python
# 根据目标用户群体推荐的 OAuth 提供商

RECOMMENDED_OAUTH_PROVIDERS = {
    # 普通消费者应用（推荐）
    "consumer": ["wechat", "alipay", "wechat_mp"],

    # 开发者/极客应用（推荐）
    "developer": ["wechat", "github", "google"],

    # 企业内部应用（推荐）
    "enterprise": ["dingtalk", "wechat_work"],

    # 年轻用户应用（推荐）
    "young": ["wechat", "qq", "wechat_mp"]
}

# PDNS 默认配置
DEFAULT_OAUTH_PROVIDERS = ["wechat", "alipay", "github", "qq"]
```

### 7.10 常见问题处理

| 问题 | 原因 | 解决方案 |
|-----|------|---------|
| 微信回调失败 | 回调域名未配置 | 在开放平台配置授权回调域名 |
| 支付宝签名错误 | 密钥格式不对 | 确保私钥格式正确（换行符处理）|
| QQ unionid 为空 | 未绑定开放平台 | 在 QQ 开放平台申请 unionid 权限 |
| 钉钉获取用户信息失败 | access_token 过期 | 重新获取 access_token |
| 微信 code 已使用 | 重复回调 | 确保 code 只使用一次 |
