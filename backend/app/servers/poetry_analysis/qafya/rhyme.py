from backend.app.utils.debate import majority_vote
from bohour.qafiah import get_qafiyah

def predict_qafya(bait):
    """
    Predict the qafya (rhyme) of the given bait (verse).

    :param bait: The verse to be analyzed.
    :return: The predicted qafya.
    """
    qafya = majority_vote(get_qafiyah([bait], short=False))[1]
    return qafya