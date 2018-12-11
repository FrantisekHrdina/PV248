
HEIGHT = 3
WIDTH = 3


class Game:

    def __init__(self):
        self.id = None
        self.name = None
        self.winner = None
        self.board = [[0 for i in range(HEIGHT)] for j in range(WIDTH)]
        self.next = 1 # Player 1 plays first
        self.has_second_player_joined = False

    def print_board(self):
        for i in range(0, HEIGHT):
            for j in range(0, WIDTH):
                print(self.board[i][j], end=' ')
            print()

    def are_all_boxes_filled(self):
        for i in range(0, HEIGHT):
            for j in range(0, WIDTH):
                if self.board[i][j] == 0:
                    return False

        return True

    def available_for_list(self):
        filled = 0
        for i in range(0, HEIGHT):
            for j in range(0, WIDTH):
                if self.board[i][j] != 0:
                    filled += 1

        return filled == 1

    def set_winner(self):
        # check rows
        for i in range(0, HEIGHT):
            if 0 != self.board[i][0] == self.board[i][1] == self.board[i][2]:
                self.winner = self.board[i][0]
                return

        # check columns
        for j in range(0, WIDTH):
            if 0 != self.board[0][j] == self.board[1][j] == self.board[2][j]:
                self.winner = self.board[0][j]
                return

        # check diagonals
        if 0 != self.board[0][0] == self.board[1][1] == self.board[2][2]:
            self.winner = self.board[0][0]
            return
        if 0 != self.board[2][0] == self.board[1][1] == self.board[0][2]:
            self.winner = self.board[2][0]
            return

        # otherwise draw
        if self.are_all_boxes_filled():
            self.winner = 0
        return

    def print_log(self):
        if self.next == 1:
            last_played = 2
        else:
            last_played = 1

        winner = 'game is not finished yet'
        if self.winner is not None:
            winner = self.winner

        last_round = 0

        for i in range(0, HEIGHT):
            for j in range(0, WIDTH):
                if self.board[i][j] != 0:
                    last_round += 1

        print('-----Round ' + str(last_round) + '-----')
        print('Last played:' + str(last_played))
        print('Board: ')
        self.print_board()
        print('Next player: ' + str(self.next))
        print('Winner: ' + str(winner))
        print()
