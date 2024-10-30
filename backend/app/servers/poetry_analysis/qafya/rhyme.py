from backend.app.utils.debate import majority_vote

from bohour.qafiah import get_qafiyah

def predict_qafya(bait):
  qafya = majority_vote(get_qafiyah([bait], short=False))[1]
  return qafya
