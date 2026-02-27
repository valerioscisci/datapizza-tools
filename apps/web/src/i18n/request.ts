import { getRequestConfig } from 'next-intl/server';

const TRANSLATION_FILES = [
  'common', 'auth', 'home', 'applications', 'talents',
  'craft-your-developer', 'jobs', 'news', 'courses',
  'profile', 'proposals', 'industry', 'notifications', 'skill-gap'
];

export default getRequestConfig(async ({ requestLocale }) => {
  const locale = await requestLocale || 'it';

  const modules = await Promise.all(
    TRANSLATION_FILES.map(file => import(`../../messages/${locale}/${file}.json`))
  );

  const messages: Record<string, unknown> = {};
  for (const mod of modules) {
    Object.assign(messages, mod.default);
  }

  return { locale, messages };
});
