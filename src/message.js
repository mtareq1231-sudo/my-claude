/**
 * Builds the welcome text sent to the customer.
 *
 * The message is deliberately short — a greeting, the website, the phone
 * number. Details like shipping and warranty live behind optional fields that
 * are empty by default: fill one in config/business.json and its line appears,
 * blank it out and the line disappears. A field may also hold an array, which
 * renders as bullets under its label.
 */
function optionalLine(icon, label, value) {
  if (!value || (Array.isArray(value) && value.length === 0)) return [];
  if (!Array.isArray(value)) return [`${icon} ${label}: ${value}`];
  return [`${icon} ${label}:`, ...value.map((item) => `   • ${item}`)];
}

export function buildWelcomeMessage(business) {
  const lines = [];

  lines.push(business.storeName ? `أهلاً بك في ${business.storeName} 👋` : 'أهلاً بك 👋');
  lines.push('شكراً لتواصلك معنا.');
  lines.push('');

  // The website is the call to action, so it gets the invitation and a line of
  // its own — on its own line the URL is a bigger tap target, and chat clients
  // are far more likely to attach a link preview card to it.
  if (business.website) {
    lines.push('🌐 تصفّح موقعنا واكتشف جميع منتجاتنا:');
    lines.push(business.website);
    lines.push('');
  }

  // The phone is the fallback, not the ask: one short line, no invitation.
  if (business.phone) {
    lines.push(`📞 للاستفسار: ${business.phone}`);
  }

  const extras = [
    ...optionalLine('🚚', 'مدة التوصيل', business.shipping),
    ...optionalLine('🛡️', 'الكفالة', business.warranty),
    ...optionalLine('🔄', 'الاسترجاع والاستبدال', business.returns),
    ...optionalLine('🕐', 'أوقات العمل', business.workingHours),
  ];
  if (extras.length) {
    lines.push('');
    lines.push(...extras);
  }

  if (business.closingLine) {
    lines.push('');
    lines.push(business.closingLine);
  }

  return lines.join('\n');
}
