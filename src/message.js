/**
 * Builds the welcome text sent to the customer.
 *
 * Every line is optional: leave a field out of config/business.json (or set it
 * to an empty string) and its line disappears from the message.
 */
export function buildWelcomeMessage(business) {
  const lines = [];

  const greeting = business.storeName
    ? `أهلاً بيك في ${business.storeName} 👋`
    : 'أهلاً بيك 👋';
  lines.push(greeting);
  lines.push('شكراً لتواصلك معانا، دي كل التفاصيل اللي محتاجها:');
  lines.push('');

  if (business.website) lines.push(`🌐 الموقع: ${business.website}`);
  if (business.phone) lines.push(`📞 رقم التواصل: ${business.phone}`);
  if (business.whatsapp && business.whatsapp !== business.phone) {
    lines.push(`💬 واتساب: ${business.whatsapp}`);
  }
  if (business.shipping) lines.push(`🚚 مدة الشحن: ${business.shipping}`);
  if (business.warranty) lines.push(`🛡️ الضمان: ${business.warranty}`);
  if (business.workingHours) lines.push(`🕐 مواعيد العمل: ${business.workingHours}`);

  if (business.closingLine) {
    lines.push('');
    lines.push(business.closingLine);
  }

  return lines.join('\n');
}
