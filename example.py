from instagram_bot import InstagramBot


def main():
    bot = InstagramBot(
        login='login', password='password', target='account_name_of_your_gf'
    )
    bot.like_all_users_media()


if __name__ == '__main__':
    main()
