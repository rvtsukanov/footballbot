SESSION_INDEX_CREATE_SCRIPT = """CREATE TABLE IF NOT EXISTS public.session_index
(
            session_id integer NOT NULL DEFAULT nextval('session_index_session_id_seq'::regclass),
            session_start_time timestamp without time zone,
            session_expire_time timestamp without time zone,
            CONSTRAINT session_index_pkey PRIMARY KEY (session_id)
)    """


SESSION2PLAYERS_CREATE_SCRIPT = '''
            CREATE TABLE IF NOT EXISTS public.sessions2players
        (
            game_date date NOT NULL,
            "out" boolean,
            username text COLLATE pg_catalog."default",
            now timestamp without time zone,
            session_id integer
        )

        TABLESPACE pg_default;

        ALTER TABLE public.sessions2players
            OWNER to rvtsukanov;
    '''


GAMES_CREATE_SCRIPT = '''
    CREATE TABLE IF NOT EXISTS public.games
    (
        game_date date NOT NULL,
        cost numeric,
        team_a boolean,
        team_b boolean,
        team_c boolean,
        team_d boolean,
        username "char"[]
    )

    TABLESPACE pg_default;

    ALTER TABLE public.games
        OWNER to rvtsukanov;
        '''
