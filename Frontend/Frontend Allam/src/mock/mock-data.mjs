// mock-data.mjs

export const mockResponses = {
  // Mock responses for category 1
  category1: [
    {
      request: { text: 'ما هو معنى هذا البيت؟' },
      response: { analysis: 'هذا البيت يمثل الأمل واليأس.' },
    },
    {
      request: { text: 'حلل لي هذا البيت' },
      response: { analysis: 'البيت يعبر عن الحب والفقدان.' },
    },
  ],

  // Mock responses for category 2
  category2: [
    {
      request: { prompt: 'صف لي الشاعر', poet1: 'المتنبي' },
      response: { bait: 'الشاعر المتنبي معروف بفصاحته.' },
    },
    {
      request: { prompt: 'اعطني بيت شعر', poet1: 'أحمد شوقي' },
      response: { bait: 'قال الشاعر أحمد شوقي ذات مرة...' },
    },
  ],

  // Mock responses for category 3
  category3: [
    {
      request: {
        poet1: 'المتنبي',
        poet2: 'أحمد شوقي',
        topics: 'الشجاعة',
      },
      response: {
        poet1: 'المتنبي يقدم بيت شعر قوي عن الشجاعة',
        poet2: 'أحمد شوقي يرد عليه بإبداع',
        judge: 'المتنبي فاز',
      },
    },
    {
      request: { poet1: 'شاعر أ', poet2: 'شاعر ب', topics: 'الحب' },
      response: {
        poet1: 'شاعر أ يتحدث عن الحب الأبدي',
        poet2: 'شاعر ب يرد عن الحب الزائل',
        judge: 'شاعر ب فاز',
      },
    },
  ],
};
