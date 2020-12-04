import find_component


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

print(bcolors.WARNING + r"""\
      ______________________________    . \  | / .
     /                            / \     \ \ / /
    |                            | ==========  - -
     \____________________________\_/     / / \ \
  ______________________________      \  | / | \
 /                            / \     \ \ / /.   .
|                            | ==========  - -
 \____________________________\_/     / / \ \    /
      ______________________________   / |\  | /  .
     /                            / \     \ \ / /
    |                            | ==========  -  - -
     \____________________________\_/     / / \ \
                                        .  / | \  .
                """ + bcolors.ENDC)


howManyProductsCompare = int(input("Kolikrát mám vzít produktů od jednoho typu komponentu: "))

scrap_core = find_component.Component_scrap_core()

components = scrap_core.hey_spock_beam_my_pc_up(howManyProductsCompare)