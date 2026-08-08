/**
 * Builds the welcome text sent to the customer.
 *
 * Every field is optional: leave it out of config/business.json (or set it to
 * an empty string) and its line disappears from the message. A field may also
 * hold an array, which renders as a bulleted list under its label — useful for
 * things like per-region delivery times.
 */
function line(icon, label, value) {
  if (!value || (Array.isArray(value) && value.length === 0)) return [];
  if (!Array.isArray(value)) return [`${icon} ${label}: ${value}`];
  return [`${icon} ${label}:`, ...value.map((item) => `   • ${item}`)];
}

export function buildWelcomeMessage(business) {
  const lines = [];

  lines.push(business.storeName ? `أهلاً بك في ${business.storeName} 👋` : 'أهلاً بك 👋');
  lines.push('شكراً لتواصلك معنا، إليك كل التفاصيل:');
  lines.push('');

  lines.push(...line('🌐', 'الموقع', business.website));
  lines.push(...line('📞', 'للتواصل', business.phone));
  if (business.whatsapp && business.whatsapp !== business.phone) {
    lines.push(...line('💬', 'واتساب', business.whatsapp));
  }
  lines.push(...line('🚚', 'مدة التوصيل', business.shipping));
  lines.push(...line('🛡️', 'الكفالة', business.warranty));
  lines.push(...line('🔄', 'الاسترجاع والاستبدال', business.returns));
  lines.push(...line('🕐', 'أوقات العمل', business.workingHours));

  if (business.closingLine) {
    lines.push('');
    lines.push(business.closingLine);
  }

  return lines.join('\n');
}
