      *----------------------------------------------------------------*
      * REMESSA SGC -> COBRANCA MAINFRAME            LRECL=200         *
      * VERSAO 03 - 2014-05                                            *
      *----------------------------------------------------------------*
       01  REG-HEADER.
           05  HDR-TIPO              PIC X(01)  VALUE '0'.
           05  HDR-DATA              PIC 9(08).
           05  HDR-AGENCIA           PIC 9(04).
           05  HDR-CONTA             PIC 9(07).
           05  HDR-NOME-CEDENTE      PIC X(30).
           05  HDR-SEQUENCIAL        PIC 9(06).
           05  FILLER                PIC X(144).
       01  REG-DETALHE.
           05  DET-TIPO              PIC X(01)  VALUE '1'.
           05  DET-NOSSO-NUMERO      PIC 9(12).
           05  DET-TIPO-DOC          PIC 9(01).
           05  DET-DOCUMENTO         PIC 9(14).
           05  DET-NOME-SACADO       PIC X(30).
           05  DET-VENCIMENTO        PIC 9(08).
           05  DET-VALOR             PIC 9(11)V99.
           05  DET-EMISSAO           PIC 9(08).
           05  DET-ESPECIE           PIC X(02).
           05  FILLER                PIC X(111).
       01  REG-TRAILER.
           05  TRL-TIPO              PIC X(01)  VALUE '9'.
           05  TRL-QTD-REGISTROS     PIC 9(06).
           05  TRL-VALOR-TOTAL       PIC 9(15)V99.
           05  FILLER                PIC X(176).
