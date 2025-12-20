import re

def filtrar_dataframe(df, filtro):
    filtro = filtro.lower().strip()
    if filtro:
        pattern = '.*'.join(map(re.escape, filtro.split()))
        df_filtrado = df[df['Descrição'].str.contains(pattern, case=False, na=False)]
    else:
        df_filtrado = df
    return df_filtrado

def calcular_total(app):
    total = 0
    for item in app.tree_selecionados.get_children():
        valores = app.tree_selecionados.item(item, 'values')
        try:
            total += float(valores[2])
        except:
            pass
    app.label_total_valor.config(text=f"R${total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
