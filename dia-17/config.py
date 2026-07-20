TOP_N = 5

ACOES_LIST = [
    "ABCB4", "ABEV3", "AFLT3", "AGRO3", "ALOS3", "ALPA4", "ALPK3", "ALUP11", "ANIM3", "ARML3",
    "ASAI3", "AUAU3", "AXIA3", "AZZA3", "BAZA3", "B3SA3", "BBAS3", "BBDC3", "BBSE3", "BEES3",
    "TOTS3", "TPIS3", "TRIS3", "TTEN3", "UGPA3", "UNIP6", "USIM5", "VALE3", "VAMO3", "VBBR3",
    "VITT3", "VIVA3", "VIVT3", "VLID3", "VSTE3", "VTRU3", "VULC3", "WEGE3", "WHRL4", "WIZC3",
    "WLMM3", "YDUQ3",
]

FIIS_LIST = [
    "ADSH11", "AERO11", "AFHF11", "AFHI11", "AIEC11", "AJFI11", "ALZM11", "ALZR11", "ASRF11", "AZPL11",
    "BBFO11", "BCIA11", "BDIF11", "BICE11", "BIPD11", "BISE11", "BMLT11", "BODI11", "BPFF11", "BRCO11",
    "CPTS11", "CPUR11", "CXAG11", "CXCI11", "CXCO11", "CYCR11", "DIVS11", "VGIP11", "VIGT11", "VILG11",
    "VINF11", "VINO11", "VISC11", "VPPR11", "VRTA11", "VVRI11", "VXXV11", "WHGR11", "XLPR11", "XPCI11",
    "XPIE11", "XPIN11", "XPLG11", "XPML11", "XPSF11",
]
##############################################################################
# Abaixo tem a lista mais completas de ações e fiis, caso queira usar completo basta descomentar e comentar as lista abaixo e comentando a de cima que é mais reduzida, para não demorar tanto tempo para buscar os dados.
# para comentar tecle ctrl + / no bloco de código que deseja comentar, e para descomentar faça o mesmo processo.
#############################################################################
# ACOES_LIST = [
#     "ABCB4", "ABEV3", "AFLT3", "AGRO3", "ALOS3", "ALPA4", "ALPK3", "ALUP11", "ANIM3", "ARML3",
#     "ASAI3", "AUAU3", "AXIA3", "AZZA3", "BAZA3", "B3SA3", "BBAS3", "BBDC3", "BBSE3", "BEES3",
#     "BEEF3", "BGIP4", "BLAU3", "BMEB4", "BMGB4", "BMOB3", "BNBR3", "BPAC11", "BRAP4", "BRAV3",
#     "BRBI11", "BRST3", "BSLI3", "BRSR6", "CAMB3", "CAML3", "CASN3", "CBAV3", "CEAB3", "CEBR3",
#     "CEEB3", "CEGR3", "CGAS3", "CGRA4", "CLSC4", "CMIG4", "CMIN3", "COCE5", "COGN3", "CPFE3",
#     "CPLE3", "CRFB3", "CSED3", "CSMG3", "CSNA3", "CSUD3", "CURY3", "CXSE3", "DESK3", "DEXP3",
#     "DIRR3", "DOHL4", "ECOR3", "EGIE3", "EKTR3", "EMBJ3", "ENGI11", "ENMT4", "EQMA3", "EQPA3",
#     "EQTL3", "EUCA3", "EVEN3", "EZTC3", "FESA4", "FIQE3", "FLRY3", "FRAS3", "GGBR3", "GGPS3",
#     "GMAT3", "GOAU4", "GPAR3", "GRND3", "HYPE3", "IGTI3", "INTB3", "IRBR3", "ISAE4", "ITSA4",
#     "ITUB4", "JHSF3", "JSLG3", "KEPL3", "KLBN11", "LAVV3", "LEVE3", "LOGG3", "LREN3", "LWSA3",
#     "MATD3", "MDIA3", "MDNE3", "MELK3", "MGLU3", "MILS3", "MLAS3", "MOTV3", "MRSA3", "MTRE3",
#     "MTSA4", "MOVI3", "MULT3", "MYPK3", "ODPV3", "OFSA3", "OPCT3", "PASS3", "PATI3", "PEAB3",
#     "PFRM3", "PGMN3", "PINE4", "PLPL3", "PNVL3", "POMO4", "POSI3", "PSSA3", "QUAL3", "RADL3",
#     "RAIL3", "RANI3", "RDOR3", "RECV3", "REDE3", "RENT3", "RIAA3", "ROMI3", "RPAD3", "SANB11",
#     "SAPR11", "SAUD3", "SBFG3", "SBSP3", "SCAR3", "SEER3", "SHUL4", "SIMH3", "SLCE3", "SMFT3",
#     "SMTO3", "SOJA3", "SUZB3", "SYNE3", "TAEE11", "TASA3", "TECN3", "TFCO4", "TGMA3", "TIMS3",
#     "TOTS3", "TPIS3", "TRIS3", "TTEN3", "UGPA3", "UNIP6", "USIM5", "VALE3", "VAMO3", "VBBR3",
#     "VITT3", "VIVA3", "VIVT3", "VLID3", "VSTE3", "VTRU3", "VULC3", "WEGE3", "WHRL4", "WIZC3",
#     "WLMM3", "YDUQ3",
# ]

# FIIS_LIST = [
#     "ADSH11", "AERO11", "AFHF11", "AFHI11", "AIEC11", "AJFI11", "ALZM11", "ALZR11", "ASRF11", "AZPL11",
#     "BBFO11", "BCIA11", "BDIF11", "BICE11", "BIPD11", "BISE11", "BMLT11", "BODI11", "BPFF11", "BRCO11",
#     "BRCR11", "BRIX11", "BROF11", "BRZP11", "BSLT11", "BTAL11", "BTCI11", "BTHF11", "BTLG11", "BTML11",
#     "BTRA11", "BTWR11", "CCME11", "CCVA11", "CLIN11", "COPN11", "CPFF11", "CPLG11", "CPOF11", "CPSH11",
#     "CPTS11", "CPUR11", "CXAG11", "CXCI11", "CXCO11", "CYCR11", "DIVS11", "DVLP11", "DVLT11", "ENDD11",
#     "EQIN11", "ERCR11", "ERPA11", "FATN11", "FCFL11", "FIGS11", "FIIB11", "FIIP11", "FTCE11", "FYTO11",
#     "GAME11", "GARE11", "GGRC11", "GRAV11", "GRUL11", "GSFI11", "GTWR11", "HBCR11", "HDOF11", "HFOF11",
#     "HGBS11", "HGCR11", "HGLG11", "HGRE11", "HGRU11", "HJCT11", "HOFC11", "HREC11", "HSAF11", "HSLG11",
#     "HSML11", "HSRE11", "HTMX11", "IBBP11", "ICRI11", "IFRA11", "INDE11", "INLG11", "ISEN11", "ISNN11",
#     "ISNT11", "ISTT11", "ITIP11", "ITIT11", "ITRI11", "JCCJ11", "JSAF11", "JSCR11", "JSRE11", "JURO11",
#     "KCRE11", "KDIF11", "KDOL11", "KFOF11", "KISU11", "KNCA11", "KNCR11", "KNHF11", "KNHY11", "KNIP11",
#     "KNOX11", "KNRI11", "KNSC11", "KNUQ11", "LASC11", "LKDV11", "LVBI11", "MANA11", "MCCI11", "MCLO11",
#     "MCRE11", "MMVE11", "MXRF11", "NCHB11", "NEWL11", "NEXG11", "NMKS11", "NUIF11", "OGIN11", "OUFF11",
#     "OXRL11", "PCIP11", "PICE11", "PLAG11", "PLCR11", "PMIS11", "PMLL11", "PNPR11", "PORD11", "PPEI11",
#     "PRIF11", "PSEC11", "PVBI11", "RBED11", "RBFM11", "RBRK11", "RBRL11", "RBRP11", "RBRR11", "RBRX11",
#     "RBVA11", "RCRB11", "RDIV11", "RECR11", "RECT11", "RELG11", "RINV11", "RVBI11", "RZAT11", "RZLC11",
#     "RZTR11", "SARE11", "SNCI11", "SNEL11", "SNFF11", "SNFZ11", "SPDE11", "SPGM11", "SPMO11", "SUIN11",
#     "TEPP11", "TRXF11", "TVRI11", "VANG11", "VCJR11", "VCRR11", "VGII11", "VGIP11", "VIGT11", "VILG11",
#     "VINF11", "VINO11", "VISC11", "VPPR11", "VRTA11", "VVRI11", "VXXV11", "WHGR11", "XLPR11", "XPCI11",
#     "XPIE11", "XPIN11", "XPLG11", "XPML11", "XPSF11",
# ]
