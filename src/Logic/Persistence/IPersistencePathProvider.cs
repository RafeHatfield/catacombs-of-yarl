namespace CatacombsOfYarl.Logic.Persistence;

public interface IPersistencePathProvider
{
    string GetMainSaveFilePath();
    string GetDailySeedsFilePath();
    string GetSettingsFilePath();
    string GetBackupDirectory();
}
