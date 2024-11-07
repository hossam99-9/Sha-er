from backend.app.agents.base_agent import BaseAgent

class PoetryCriticAgent(BaseAgent):
    def __init__(self, critic_model):
        self.critic_model = critic_model

    def _prepare_critic_prompt(self, bait):
      critic_prompt = """
      <s> [INST]<<SYS>>
      أنت محلل للشعر العربي و دورك أن تحلل البيت بناء علي اختيار الكلمات و المعني و الأسلوب.
      سأعطيك بيت شعر و أنت تعطيني نحليل منظم للبيت
      The INST block will always be a json string:
      {
          "prompt": {البيت}
      }
      <</SYS>>
      أعطيني النقد فقط لا تقوم بكتابة أي شيء اخر
      [/INST]
      """

      instruction_prompt = f"""
      [INST] 
      {{
          "prompt": "{bait}"
      }}
      [/INST]
      """
      return critic_prompt + instruction_prompt
    
    def critic(self, bait):
        prompt = self._prepare_critic_prompt(bait)
        criticism = self.critic_model.generate(prompt)
        return criticism