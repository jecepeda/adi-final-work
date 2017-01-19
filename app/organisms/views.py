from . import organisms
from ..models import Organism

@organisms.route('/organisms/', methods=['POST'])
def put_organism():
