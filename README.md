# my-claude

## ربط Meta Pixel بمتجر Shopify (Warmup — warmupjo.com)

الهدف: توصيل أحداث المتجر لبيكسل يقدر حساب **habibi** الإعلاني (1932190657582170) يستخدمه.

البيكسل المستهدف: **warmup jordan** — ID: `1054515230383520`

### الطريقة الأولى (الأفضل — من غير كود)

من تطبيق **Facebook & Instagram** جوه Shopify:

1. Shopify admin → **Settings → Apps and sales channels → Facebook & Instagram**
2. **Settings → Data sharing**
3. غيّر البيكسل المختار إلى **warmup jordan** (1054515230383520)

دي بتدّي تغطية كاملة للأحداث بما فيها **Purchase** عن طريق Conversions API.

### الطريقة الثانية (كود في الثيم)

لو عايز الحقن اليدوي بدل التطبيق:

1. Shopify admin → **Online Store → Themes → ⋯ → Edit code** (الثيم المنشور: "Warmup staging (hero edits)")
2. من **Snippets → Add a new snippet** باسم `meta-pixel` والصق محتوى الملف [`snippets/meta-pixel.liquid`](snippets/meta-pixel.liquid)
3. افتح `layout/theme.liquid` وضيف السطر ده قبل `{{ content_for_header }}` مباشرة:

   ```liquid
   {% render 'meta-pixel' %}
   ```

تغطية الطريقة دي: PageView, ViewContent, Search, AddToCart, InitiateCheckout.
**Purchase مش هيشتغل** من كود الثيم لأن صفحات الـ checkout مقفولة — عشان كده الطريقة الأولى أفضل.

### التحقق بعد التركيب

- افتح [Meta Events Manager](https://business.facebook.com/events_manager2) → اختار البيكسل → **Test Events** واتصفح warmupjo.com
- أو ركّب إضافة Meta Pixel Helper في كروم
