USE [Baza_licytacji_lasow]
GO

/****** Object:  Table [dbo].[AUKCJE_LASY]    Script Date: 19.07.2023 17:30:48 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[AUKCJE_LASY](
	[AUK_ID] [int] IDENTITY(1,1) NOT NULL,
	[AUK_LINK] [varchar](100) NULL,
	[AUK_DATA] [varchar](60) NULL,
	[AUK_CENA_WYWOLAWCZA] [varchar](20) NULL,
	[AUK_HTML] [varchar](max) NULL,
	[AUK_AKTUALNA] [bit] NULL,
	[AUK_KLUCZ] [varchar](30) NULL,
	[AUK_DATA_BIN] [date] NULL,
	[AUK_CENA_WYWOLAWCZA_NUM] [decimal](20, 2) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO


