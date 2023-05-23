export function Document({extension, name, onClick}) {

    return (
        <div className="document-container" onClick={onClick}>
            <div className="document-background">
                <img src={require(`../assets/${extension}.png`)} alt="" className="document-icon" />
            </div>
            <div className="document-name">{name.split("_").slice(1).join("_")}</div>
        </div>
    );
}